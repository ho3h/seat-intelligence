"""RECON-SWING template library (runs/exp10). Hand-designed HVM2 text generators; nothing is learned or searched.
Builds on runs/exp5/lib.py (stream, nav) and runs/exp5/trie.hvm.txt (lg, zt, cnt, ins).

The central template is `cc_core(p, op)`: connected components by label propagation over PRE-WIRED CHANNELS.

  What it computes. Every vertex i of 0..2^L-1 holds a label x (initially x0(i) = base + i*stride). Each round every
  vertex sends x to all its neighbours and replaces x by op(x, received...) with op = max (@mx) or min (@mn). Rounds
  repeat until no label changes (a global OR). The result is a depth-L trie whose leaf i is (x ch): x the final label
  (max- or min-member of i's component when x0(i) = i), ch the vertex's channel list (erase it when done).

  Why it is shallow. The edge list is read once by the blocked stream walker (~2.3 rounds/edge, the input floor). For
  each edge (u, v) the walker creates two fresh wires c1, c2 and pushes the channel ends (in out) = (c2 c1) onto
  leaf u and (c1 c2) onto leaf v with pre-expanded keyed pushes (nav). A channel is a stream: the producer writes
  `o ~ (x next)`, the consumer reads `i ~ (y rest)`; both ends are the same wire, so one CON~CON annihilation moves
  the value, and `next`/`rest` become the next round's wire. No keyed update, no trie routing, no gated emission
  happens inside the rounds: a round is one trie traversal (switch on L per level), a walk of each vertex's channel
  list (send, receive, running op), and an OR-reduce of the change flags.

  Cost (measured, n = 72..144): cc_core ~105 depth per synchronous round at low degree (trie descent + global OR);
  cc_pipe ~20 per round at degree 2, ~15 + 4-6*deg_max in general, plus k speculative rounds. Rounds = the LP round
  count R (max distance from a vertex to its component's extreme member) + 1. Work per round O(n + m).

  Port conventions (all tuples right-nested as in PHYSICS.md):
    @{p}_cc  ~ (L (es Sf))          es: list of (u v) pairs, u, v < 2^L. Labels start at i (stride 1).
    @{p}_cct ~ (L (tau (es Sf)))    es: list of (u (v s)) triples; an edge is live iff s >= tau. Dead edges get a
                                    constant neutral stream (@{p}_zs) so every channel list stays uniform.
    Sf leaves: (x ch).
  Rejected edges cost the same as accepted ones (no switch sits on the stream's critical chain).

Other templates here:
  tl_leafmap(p, fn)  : trie of (x ch) leaves -> list of fn(x, i) for i < n (tail threaded, all cells in parallel).
  cnt_trie(p)        : scatter-count: count[x] += 1 for every leaf (x ch) (keyed incs pre-expanded once x is known).
  get(p)             : keyed read of one leaf (value, trie') for lookups (nav instance).
"""
import os, sys
D5 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exp5")
sys.path.insert(0, D5)
from lib import stream, nav  # noqa: E402

TRIE = open(os.path.join(D5, "trie.hvm.txt")).read()

MX = """// mx(a, b) = max, mn(a, b) = min
@mx = (a (b o))
  & a ~ {a1 a2}
  & b ~ {b1 b2}
  & a1 ~ $([<] $(b1 lt))
  & lt ~ ?((@mx_a @mx_b) (a2 (b2 o)))
@mx_a = (a (* a))
@mx_b = (* (* (b b)))
@mn = (a (b o))
  & a ~ {a1 a2}
  & b ~ {b1 b2}
  & a1 ~ $([<] $(b1 lt))
  & lt ~ ?((@mx_b0 @mx_a0) (a2 (b2 o)))
@mx_a0 = (* (a (* a)))
@mx_b0 = (* (b b))
"""

MK = """// mk(L, base, stride): trie of depth L whose leaf i is (base + i*stride, [])
@mk = (L (base (st o)))
  & L ~ ?((@mk_leaf @mk_node) (base (st o)))
@mk_leaf = (b (* (b (0 *))))
@mk_node = (lm (base (st (a c))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {b1 b2}
  & st ~ {s1 {s2 s3}}
  & 1 ~ $([<<] $(l3 half))
  & half ~ $([*] $(s3 off))
  & b2 ~ $([+] $(off bR))
  & @mk ~ (l1 (b1 (s1 a)))
  & @mk ~ (l2 (bR (s2 c)))
@zl = (?(((0 *) @zl_node) o) o)
@zl_node = (lm (a b))
  & lm ~ {l1 l2}
  & @zl ~ (l1 a)
  & @zl ~ (l2 b)
// cp: push a channel pair onto leaf k's channel list
@cp_act = ((x lst) (P (x (1 (P lst)))))
// cq: push (r P): P is pushed iff r == 0 (r = "rejected"); a rejected channel is erased at both ends
@cq_act = ((x lst) ((r P) (x l2)))
  & r ~ ?(((q (m (1 (q m)))) (* (* (k k)))) (P (lst l2)))
"""


SEL = {"mx": "((a (* a)) (* (* (b b))))", "mn": "((* (b b)) (* (a (* a))))"}


def cc_core(p, op, neutral, K=16):
    """Label propagation over pre-wired channels (see module docstring). op: 'mx' or 'mn'. neutral: the value a dead
    channel delivers (0 for max, 16777215 for min)."""
    return f"""// ---- cc core {p} (op {op})
@{p}_cc = (L (es Sf))
  & L ~ {{L1 {{L2 L3}}}}
  & @mk ~ (L1 (0 (1 S0)))
  & @{p}_ea_blk ~ (es ((L2 S0) S))
  & @{p}_loop ~ (L3 (S Sf))
@{p}_cct = (L (tau (es Sf)))
  & L ~ {{L1 {{L2 L3}}}}
  & @mk ~ (L1 (0 (1 S0)))
  & @{p}_et_blk ~ (es (((L2 tau) S0) S))
  & @{p}_loop ~ (L3 (S Sf))
@{p}_ea_step = ((L s) ((u v) (L3 s2)))
  & L ~ {{L1 {{L2 L3}}}}
  & @cp ~ (s (u (L1 ((c2 c1) s1))))
  & @cp ~ (s1 (v (L2 ((c1 c2) s2))))
@{p}_ea_fin = ((* s) s)
@{p}_et_step = (((L tau) s) ((u (v sc)) ((L3 tau3) s2)))
  & L ~ {{L1 {{L2 L3}}}}
  & tau ~ {{t1 tau3}}
  & sc ~ $([<] $(t1 rej))
  & rej ~ {{r1 r2}}
  & @cq ~ (s (u (L1 ((r1 (c2 c1)) s1))))
  & @cq ~ (s1 (v (L2 ((r2 (c1 c2)) s2))))
@{p}_et_fin = ((* s) s)
@{p}_ch_acc = ((c2 c1) (c1 c2))
@{p}_ch_rej = (* ((@{p}_zs *) (@{p}_zs *)))
@{p}_zs = ({neutral} @{p}_zs)
@{p}_loop = (L (S o))
  & L ~ {{L1 L2}}
  & @{p}_rnd ~ (L1 (S (S2 f)))
  & f ~ ?((@{p}_done @{p}_again) (L2 (S2 o)))
@{p}_done = (* (S S))
@{p}_again = (* (L (S o)))
  & @{p}_loop ~ (L (S o))
@{p}_rnd = (L (S (S2 f)))
  & L ~ ?((@{p}_rnd_leaf @{p}_rnd_node) (S (S2 f)))
@{p}_rnd_node = (lm ((a b) ((a2 b2) f)))
  & lm ~ {{l1 l2}}
  & @{p}_rnd ~ (l1 (a (a2 f1)))
  & @{p}_rnd ~ (l2 (b (b2 f2)))
  & f1 ~ $([|] $(f2 f))
@{p}_rnd_leaf = ((x ch) ((x2 ch2) f))
  & x ~ {{xs {{xa xc}}}}
  & @{p}_wk ~ (ch (xs (xa (ch2 m))))
  & m ~ {{x2 m2}}
  & m2 ~ $([!] $(xc f))
@{p}_wk = ((?((@{p}_wk_nil @{p}_wk_cons) (pl (x (acc (ch2 m))))) pl) (x (acc (ch2 m))))
@{p}_wk_nil = (* (* (acc ((0 *) acc))))
@{p}_wk_cons = (* (((i o) rest) (x (acc ((1 ((i2 o2) rest2)) m)))))
  & x ~ {{x1 x2}}
  & o ~ (x1 o2)
  & i ~ (y i2)
  & acc ~ {{a1 a2}}
  & y ~ {{b1 b2}}
  & a1 ~ $([<] $(b1 lt))
  & lt ~ ?({SEL[op]} (a2 (b2 acc1)))
  & @{p}_wk ~ (rest (x2 (acc1 (rest2 m))))
""" + stream(f"{p}_ea", K, f"{p}_ea_step", f"{p}_ea_fin") + stream(f"{p}_et", K, f"{p}_et_step", f"{p}_et_fin")


def cc_pipe(p, op, neutral, k=2, K=16):
    """Pipelined variant of cc_core with NO global barrier per round (same ports: @{p}_cc, @{p}_cct -> Sf).
    Every vertex is a persistent process (@{p}_lf) that loops on its own: round r runs iff decision D_r = 1, where the
    decision stream D = [1]*k ++ [f_0, f_1, ...] and f_j = OR over vertices of 'label changed in round j'. The OR is
    computed by persistent up-loop processes (@{p}_up, one per trie node, tagged flag streams), the root turns flags into
    decisions (@{p}_rt), and persistent down-loops (@{p}_dn) broadcast them. Because a vertex waits for decision j only
    at round j+k, the ~4L-deep reduce/broadcast latency overlaps k rounds of useful work, and the per-round depth is the
    vertex's own round (walk of its channel list). Cost: k extra (idempotent) rounds of work; depth about
    (R + k) * T_leaf + 4L, T_leaf ~ 15 + 6*deg_max."""
    ones = "".join("(1 " for _ in range(k)) + "D3" + ")" * k
    base = cc_core(p, op, neutral, K)
    base = base.replace(f"""@{p}_loop = (L (S o))
  & L ~ {{L1 L2}}
  & @{p}_rnd ~ (L1 (S (S2 f)))
  & f ~ ?((@{p}_done @{p}_again) (L2 (S2 o)))
@{p}_done = (* (S S))
@{p}_again = (* (L (S o)))
  & @{p}_loop ~ (L (S o))
""", f"""@{p}_loop = (L (S O))
  & @{p}_spawn ~ (L (S (D (F O))))
  & D ~ {ones}
  & @{p}_rt ~ (F D3)
@{p}_spawn = (L (S (D (F O))))
  & L ~ ?((@{p}_sp_leaf @{p}_sp_node) (S (D (F O))))
@{p}_sp_leaf = ((x ch) (D (F O)))
  & @{p}_lf ~ (x (ch (D (F O))))
@{p}_sp_node = (lm ((a b) (D (F (Oa Ob)))))
  & lm ~ {{l1 l2}}
  & @{p}_dn ~ (D (Da Db))
  & @{p}_up ~ (Fa (Fb F))
  & @{p}_spawn ~ (l1 (a (Da (Fa Oa))))
  & @{p}_spawn ~ (l2 (b (Db (Fb Ob))))
// vertex process: wait for the decision, then one round; emits its change flag
@{p}_lf = (x (ch (D (F out))))
  & D ~ (d D2)
  & d ~ ?((@{p}_lf_stop @{p}_lf_go) (x (ch (D2 (F out)))))
@{p}_lf_stop = (x (ch (* ((0 *) (x ch)))))
@{p}_lf_go = (* (x (ch (D2 (F out)))))
  & x ~ {{xs {{xa xc}}}}
  & @{p}_wk ~ (ch (xs (xa (ch2 m))))
  & m ~ {{x2 m2}}
  & m2 ~ $([!] $(xc f))
  & F ~ (1 (f F2))
  & @{p}_lf ~ (x2 (ch2 (D2 (F2 out))))
// up-loop: OR of two tagged flag streams (children stop together)
@{p}_up = ((?((@{p}_up_nil @{p}_up_cons) (pl (Fr Fo))) pl) (Fr Fo))
@{p}_up_nil = (* (* (0 *)))
@{p}_up_cons = (* ((f Fl) ((* (g Fr)) Fo)))
  & f ~ $([|] $(g h))
  & Fo ~ (1 (h Fo2))
  & @{p}_up ~ (Fl (Fr Fo2))
// down-loop: copy each decision to both children, stop after a 0
@{p}_dn = ((d D2) ((d1 Dl2) (d2 Dr2)))
  & d ~ {{d1 {{d2 d3}}}}
  & d3 ~ ?((@{p}_dn_stop @{p}_dn_go) (D2 (Dl2 Dr2)))
@{p}_dn_stop = (* (* *))
@{p}_dn_go = (* (D2 (Dl2 Dr2)))
  & @{p}_dn ~ (D2 (Dl2 Dr2))
// root: decision j+k = flag j; after the first 0, drop the remaining flags
@{p}_rt = ((?((@{p}_rt_nil @{p}_rt_cons) (pl D)) pl) D)
@{p}_rt_nil = (* *)
@{p}_rt_cons = (* ((f F2) D))
  & f ~ {{f1 f2}}
  & D ~ (f1 D2)
  & f2 ~ ?((@{p}_rt_stop @{p}_rt_go) (F2 D2))
@{p}_rt_stop = (* *)
@{p}_rt_go = (* (F2 D2))
  & @{p}_rt ~ (F2 D2)
""")
    assert f"@{p}_spawn" in base
    return base


def tl_leafmap(p, body):
    """@{p}_tl ~ (t (L (base (n (tail o))))): the list [f(x, i) for leaf i < n] prepended to tail, where leaves are
    (x ch). body: HVM lines computing `y` from wires `x` and `i` (each usable once). All cells are built in parallel."""
    return f"""@{p}_tl = (t (L (base (n (tail o)))))
  & L ~ ?((@{p}_tl_leaf @{p}_tl_node) (t (base (n (tail o)))))
@{p}_tl_leaf = ((x *) (base (n (tail o))))
  & base ~ {{b0 i}}
  & b0 ~ $([<] $(n keep))
  & keep ~ ?((@{p}_tl_drop @{p}_tl_keep) (y (tail o)))
{body}
@{p}_tl_drop = (* (t t))
@{p}_tl_keep = (* (x (t (1 (x t)))))
@{p}_tl_node = (lm ((a b) (base (n (tail o)))))
  & lm ~ {{l1 {{l2 l3}}}}
  & base ~ {{b1 b2}}
  & n ~ {{n1 n2}}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @{p}_tl ~ (a (l1 (b1 (n1 (mid o)))))
  & @{p}_tl ~ (b (l2 (bR (n2 (tail mid)))))
"""


INC = """// inc(t, k, L): add 1 to leaf k (pre-expanding keyed update)
@inc = (t (k (L o)))
  & L ~ ?((@inc_leaf @inc_node) (t (k o)))
@inc_leaf = (x (* o))
  & x ~ $([+1] o)
@inc_node = (lm (t (k o)))
  & k ~ {k1 k2}
  & lm ~ {l1 l2}
  & k1 ~ $([>>] $(l1 sh))
  & sh ~ $([&] $(1 b))
  & b ~ ?((@inc_L @inc_R) (t (k2 (l2 o))))
@inc_L = ((l r) (k (L (l2 r))))
  & @inc ~ (l (k (L l2)))
@inc_R = (* ((l r) (k (L (l r2)))))
  & @inc ~ (r (k (L r2)))
// scat(S, L, LL, c_in, c_out): for every leaf (x ch) of S (ch erased), count[x] += 1; count trie threaded
@scat = (S (L (LL (c co))))
  & L ~ ?((@scat_leaf @scat_node) (S (LL (c co))))
@scat_leaf = ((x *) (LL (c co)))
  & @inc ~ (c (x (LL co)))
@scat_node = (lm ((a b) (LL (c co))))
  & lm ~ {l1 l2}
  & LL ~ {LA LB}
  & @scat ~ (a (l1 (LA (c m))))
  & @scat ~ (b (l2 (LB (m co))))
"""


def get(p):
    """@{p}_get ~ (t (k (L (v t2)))): v = leaf k's label (leaves (x ch)); t2 = t unchanged."""
    return nav(f"{p}_get", f"{p}_get_act") + f"""@{p}_get_act = ((x ch) (v (x2 ch)))
  & x ~ {{v x2}}
"""


def lib():
    return MX + MK + nav("cp", "cp_act") + nav("cq", "cq_act") + TRIE
