"""RECON-SWING-2 template library (runs/exp18). Hand-designed HVM2 text; nothing is learned or searched.
Builds on genome/lib/graphprims.py (Book, lg, const_trie, update, get, fold, stream) and the channel idea of
runs/exp10 (a channel is a pair of wires used as a stream, one value per round in each direction).

Templates (each adds definitions to a graphprims Book):

  sort_scores(b)   bucket sort of candidate triples by (score desc, u asc, v asc), with a tau filter.
                   @gs_blk ~ (cs (((L tau) C0) C))   stream over cs; C0 = @gl_zl10 ~ (10 C0) (1024 empty buckets).
                   Candidate (u, v, s) goes to bucket 1000 - s as packed key pk = (u << L) | v, inserted into the
                   bucket's ascending list (sorted insert act); candidates with s < tau are dropped by the act (the
                   reject bit rides in the payload, so no switch sits on the stream's chain). Keyed updates
                   pre-expand, so the stream costs ~2.3 rounds/candidate; buckets are small (ties only).

  greedy_core(b)   the ordered constrained greedy merge (spec step 4), sequential over the sorted candidates.
                   @gr ~ (L (tau (cap (mnl (cs (Tf h))))))
                   Tf: final state trie, leaf (x (sz ch)), x = largest member of the node's cluster; h = the skipped
                   pairs (u, v) in processing order (a list; its tail is closed with Nil here).
                   State per node leaf: label x (= max member of its cluster), cluster size sz, and ch, the node's
                   list of pre-wired must-not-link channels (one channel per MNL pair, set up once from the mnl
                   stream, exactly like the edge channels of exp10's cc_core).
                   One step (candidate (u, v)) is:
                     1. A, sA = leaf u of copy trie CU; B, sB = leaf v of copy trie CV (keyed gets whose navigation
                        depends only on u, v and L, so they are pre-expanded and cost ~nothing once the leaf exists);
                     2. one traversal @rd of the state trie: A, B are broadcast to every leaf (DUP tree, ~L rounds);
                        each leaf computes w = the label a partner must carry to make this merge a conflict
                        (B if x == A, A if x == B, else 16777215), sends x on all its MNL channels, receives the
                        partners' labels and ORs (y == w); the flags are OR-reduced up the trie;
                     3. @dec: ok = A != B and no conflict and sA + sB <= cap; skip = A != B and not ok;
                        lo' = ok ? min(A, B) : 16777215, hi' = ok ? max(A, B) : 16777215, S = sA + sB;
                     4. the same traversal, on the way back down, relabels: x == lo' -> hi', and sz := S for
                        x in {lo', hi'}; it emits the next state trie plus two numeric copies (CU', CV') for the
                        next step's gets.
                   Depth per step ~ 2 broadcasts + 1 OR-reduction over the trie (~6L) + leaf work; work per step
                   O(2^L + |mnl|). Labels stay "largest member" because every merge relabels to max(A, B).
                   Duplicated candidates (pipeline kernels) are harmless: a pair skipped once is skipped again
                   (clusters only grow), and a merged pair is a no-op.

  Also: mk_leaf tries (mk_tries), channel push act (@gpc), list append (@gapp), the sorted/dedup insert acts,
  and out_labels (state trie -> first n labels as a list).
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from genome.lib.graphprims import Book, lg, const_trie, update, get, fold, stream, iota_trie, to_list  # noqa: E402,F401

BIG = 16777215


def mk_trie(b, name, leaf):
    """@name ~ (L (base t)): trie of depth L; leaf i is `leaf` with wire b = base + i (leaf is the right-hand side
    of a definition with parameter b, e.g. '(b (b 1))' means leaf (i 1))."""
    b.add(f"""
@{name} = (L (base o))
  & L ~ ?((@{name}_leaf @{name}_node) (base o))
@{name}_leaf = {leaf}
@{name}_node = (lm (base (a c)))
  & lm ~ {{l1 {{l2 l3}}}}
  & base ~ {{b1 b2}}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @{name} ~ (l1 (b1 a))
  & @{name} ~ (l2 (bR c))
""")
    return name


SORTED_INSERT = """
@gsi = ((tag pl) (k o))
  & tag ~ ?((@gsi_nil @gsi_cons) (pl (k o)))
@gsi_nil = (* (k (1 (k (0 *)))))
@gsi_cons = (* ((h t) (k o)))
  & h ~ {h1 h2}
  & k ~ {k1 k2}
  & h1 ~ $([<] $(k1 lt))
  & lt ~ ?((@gsi_front @gsi_after) (h2 (t (k2 o))))
@gsi_front = (h (t (k (1 (k (1 (h t)))))))
@gsi_after = (* (h (t (k (1 (h o2))))))
  & @gsi ~ (t (k o2))
"""

# sorted insert that drops a key equal to one already present (set semantics)
SORTED_INSERT_DEDUP = """
@gsd = ((tag pl) (k o))
  & tag ~ ?((@gsd_nil @gsd_cons) (pl (k o)))
@gsd_nil = (* (k (1 (k (0 *)))))
@gsd_cons = (* ((h t) (k o)))
  & h ~ {h1 {h2 h3}}
  & k ~ {k1 {k2 k3}}
  & h1 ~ $([<] $(k1 lt))
  & h2 ~ $([=] $(k2 eq))
  & lt ~ $([*] $(2 lt2))
  & lt2 ~ $([+] $(eq sel))
  & sel ~ ?((@gsd_front @gsd_more) (h3 (t (k3 o))))
@gsd_front = (h (t (k (1 (k (1 (h t)))))))
@gsd_more = (d (h (t (k o))))
  & d ~ ?((@gsd_eq @gsd_after) (h (t (k o))))
@gsd_eq = (h (t (* (1 (h t)))))
@gsd_after = (* (h (t (k (1 (h o2))))))
  & @gsd ~ (t (k o2))
"""

APPEND = """
@gapp = ((tag pl) (acc o))
  & tag ~ ?((@gapp_nil @gapp_cons) (pl (acc o)))
@gapp_nil = (* (a a))
@gapp_cons = (* ((h t) (acc (1 (h o2)))))
  & @gapp ~ (t (acc o2))
"""


def sort_scores(b):
    """Bucket sort by (score desc, u asc, v asc) with tau filter. See module docstring."""
    lg(b)
    const_trie(b, "gl_zl", "(0 *)")
    b.add(SORTED_INSERT)
    update(b, "gsins", """(lst ((r pk) o))
  & r ~ ?((@gsins_go @gsins_drop) (lst (pk o)))""")
    b.add("""
@gsins_go = (lst (pk o))
  & @gsi ~ (lst (pk o))
@gsins_drop = (* (lst (* lst)))
""")
    stream(b, "gs", 16, """(((L tau) C) ((u (v s)) ((L4 tau3) C2)))
  & L ~ {L1 L4}
  & tau ~ {t1 tau3}
  & s ~ {s1 {s2 s3}}
  & s1 ~ $([<] $(t1 lt))
  & lt ~ {r1 r2}
  & 1000 ~ $([-] $(s2 k0))
  & s3 ~ $([+] $(23 d))
  & r1 ~ $([*] $(d e))
  & k0 ~ $([+] $(e key))
  & u ~ $([<<] $(L1 uh))
  & uh ~ $([|] $(v pk))
  & @gsins ~ (C (key (10 ((r2 pk) C2))))""", "((* C) C)")
    return "gs_blk"


def greedy_core(b):
    """Ordered constrained greedy merge. @gr ~ (L (tau (cap (mnl (cs (Tf h)))))). See module docstring."""
    sort_scores(b)
    b.add(APPEND)
    get(b, "gget")
    mk_trie(b, "gmkT", "(b (b (1 (0 *))))")
    mk_trie(b, "gmkC", "(b (b 1))")
    # channel push onto a state leaf (x (sz ch))
    update(b, "gpc", "((x (sz lst)) (P (x (sz (1 (P lst))))))")
    stream(b, "gm", 16, """((L T) ((a b) (L3 T2)))
  & L ~ {L1 {L2 L3}}
  & @gpc ~ (T (a (L1 ((c2 c1) T1))))
  & @gpc ~ (T1 (b (L2 ((c1 c2) T2))))""", "((* T) T)")
    b.add(f"""
@gr = (L (tau (cap (mnl (cs (Tf h))))))
  & L ~ {{L1 {{L2 {{L3 {{L4 {{L5 L6}}}}}}}}}}
  & @gmkT ~ (L1 (0 T0))
  & @gmkC ~ (L2 (0 CU0))
  & @gmkC ~ (L3 (0 CV0))
  & @gm_blk ~ (mnl ((L4 T0) T1))
  & @gl_zl ~ (10 Z)
  & @gs_blk ~ (cs (((L5 tau) Z) C))
  & @gsw ~ (C (10 ((T1 (CU0 (CV0 (L6 (cap h))))) (Tf (* (* (* (* (0 *)))))))))
// fold over the 1024 score buckets, left to right, threading the greedy state
@gsw = (t (L (S So)))
  & L ~ ?((@gsw_leaf @gsw_node) (t (S So)))
@gsw_leaf = (lst (S So))
  & @gwl ~ (lst (S So))
@gsw_node = (lm ((a c) (S So)))
  & lm ~ {{l1 l2}}
  & @gsw ~ (a (l1 (S mid)))
  & @gsw ~ (c (l2 (mid So)))
@gwl = ((?((@gwl_nil @gwl_cons) (pl (S So))) pl) (S So))
@gwl_nil = (* (S S))
@gwl_cons = (* ((h t) (S So)))
  & @gst ~ (S (h S2))
  & @gwl ~ (t (S2 So))
// one greedy step for packed candidate pk = (u << L) | v
@gst = ((T (CU (CV (L (cap h))))) (pk (T2 (CU2 (CV2 (L6 (cap2 h2)))))))
  & L ~ {{L1 {{L2 {{L3 {{L4 {{L5 L6}}}}}}}}}}
  & cap ~ {{cp1 cap2}}
  & pk ~ {{pk1 pk2}}
  & pk1 ~ $([>>] $(L1 u))
  & 1 ~ $([<<] $(L2 m1))
  & m1 ~ $([-] $(1 msk))
  & pk2 ~ $([&] $(msk v))
  & u ~ {{u1 u2}}
  & v ~ {{v1 v2}}
  & @gget ~ (CU (u1 (L3 (A sA))))
  & @gget ~ (CV (v1 (L4 (B sB))))
  & A ~ {{A1 A2}}
  & B ~ {{B1 B2}}
  & @grd ~ (T (L5 (A1 (B1 (lo (hi (Ss (c (T2 (CU2 CV2))))))))))
  & @gdec ~ ((A2 (B2 (sA (sB (cp1 c))))) (lo (hi (Ss sk))))
  & sk ~ ?((@gst_keep @gst_skip) (h (h2 (u2 v2))))
@gst_keep = (h (h (* *)))
@gst_skip = (* ((1 ((u v) h2)) (h2 (u v))))
// decision
@gdec = ((A (B (sA (sB (cap c))))) (lo2 (hi2 (S sk))))
  & A ~ {{Aa {{Ab Ac}}}}
  & B ~ {{Ba {{Bb Bc}}}}
  & Aa ~ $([=] $(Ba same))
  & Ab ~ $([<] $(Bb lt))
  & lt ~ ?((@gdec_ge @gdec_lt) (Ac (Bc (lo hi))))
  & sA ~ $([+] $(sB ssum))
  & ssum ~ {{S s2}}
  & cap ~ $([<] $(s2 capf))
  & c ~ $([|] $(capf bad))
  & bad ~ {{bad1 bad2}}
  & same ~ $([=] $(0 ns))
  & ns ~ {{ns1 ns2}}
  & 1 ~ $([-] $(bad1 nb))
  & ns1 ~ $([*] $(nb ok))
  & ns2 ~ $([*] $(bad2 sk))
  & ok ~ {{ok1 ok2}}
  & lo ~ $([+1] lp)
  & lp ~ $([*] $(ok1 lq))
  & lq ~ $([+] $({BIG} lo2))
  & hi ~ $([+1] hp)
  & hp ~ $([*] $(ok2 hq))
  & hq ~ $([+] $({BIG} hi2))
@gdec_ge = (a (b (b a)))
@gdec_lt = (* (a (b (a b))))
// one round over the state trie: conflict flags up, relabel down, plus two numeric copies
@grd = (T (L (A (B (lo (hi (S (c (T2 (CU CV))))))))))
  & L ~ ?((@grd_leaf @grd_node) (T (A (B (lo (hi (S (c (T2 (CU CV))))))))))
@grd_node = (lm ((ta tb) (A (B (lo (hi (S (c ((a2 b2) ((ua ub) (va vb)))))))))))
  & lm ~ {{l1 l2}}
  & A ~ {{A1 A2}}
  & B ~ {{B1 B2}}
  & lo ~ {{lo1 lo2}}
  & hi ~ {{hi1 hi2}}
  & S ~ {{S1 S2}}
  & @grd ~ (ta (l1 (A1 (B1 (lo1 (hi1 (S1 (c1 (a2 (ua va))))))))))
  & @grd ~ (tb (l2 (A2 (B2 (lo2 (hi2 (S2 (c2 (b2 (ub vb))))))))))
  & c1 ~ $([|] $(c2 c))
@grd_leaf = ((x (sz ch)) (A (B (lo (hi (S (c ((x2 (sz2 ch2)) ((cux cus) (cvx cvs))))))))))
  & x ~ {{xa {{xb {{xc {{xd {{xe {{xf xg}}}}}}}}}}}}
  & A ~ {{Aa Ab}}
  & B ~ {{Ba Bb}}
  & xa ~ $([=] $(Aa isA))
  & xb ~ $([=] $(Ba isB))
  & Bb ~ $([+1] Bp)
  & Ab ~ $([+1] Ap)
  & isA ~ $([*] $(Bp t1))
  & isB ~ $([*] $(Ap t2))
  & t1 ~ $([+] $(t2 t3))
  & t3 ~ $([+] $({BIG} w))
  & @gcw ~ (ch (xc (w (c ch2))))
  & xd ~ $([=] $(lo mlo))
  & xg ~ $([=] $(hi1 mhi))
  & hi ~ {{hi1 hi2}}
  & hi2 ~ $([-] $(xe dd))
  & mlo ~ {{mlo1 mlo2}}
  & mlo1 ~ $([*] $(dd pp))
  & xf ~ $([+] $(pp xn))
  & xn ~ {{x2 {{cux cvx}}}}
  & mlo2 ~ $([|] $(mhi mm))
  & sz ~ {{sza szb}}
  & S ~ $([-] $(sza ds))
  & mm ~ $([*] $(ds sp))
  & szb ~ $([+] $(sp szn))
  & szn ~ {{sz2 {{cus cvs}}}}
// channel walk: send x on every MNL channel, receive the partner's label y, c = OR (y == w)
@gcw = ((?((@gcw_nil @gcw_cons) (pl (x (w (c ch2))))) pl) (x (w (c ch2))))
@gcw_nil = (* (* (* (0 (0 *)))))
@gcw_cons = (* (((i o) rest) (x (w (c (1 ((i2 o2) rest2)))))))
  & x ~ {{x1 x2}}
  & w ~ {{w1 w2}}
  & o ~ (x1 o2)
  & i ~ (y i2)
  & y ~ $([=] $(w1 e))
  & e ~ $([|] $(c2 c))
  & @gcw ~ (rest (x2 (w2 (c2 rest2))))
""")
    return "gr"


def out_labels(b):
    """@gout ~ (T (L (0 (n (tail o))))): first n labels of a state trie (leaves (x (sz ch)); sz, ch erased)."""
    b.add("""
@gout_drop = (* (t t))
@gout_keep = (* (x (t (1 (x t)))))
""")
    return fold(b, "gout", """((x *) (i (n (acc o))))
  & i ~ $([<] $(n keep))
  & keep ~ ?((@gout_drop @gout_keep) (x (acc o)))""")


# ---------------------------------------------------------------------------------------------- keyed-bucket outputs
COUNT_INSERT = """
@gci = ((tag pl) (k o))
  & tag ~ ?((@gci_nil @gci_cons) (pl (k o)))
@gci_nil = (* (k (1 ((k 1) (0 *)))))
@gci_cons = (* (((h c) t) (k o)))
  & h ~ {h1 {h2 h3}}
  & k ~ {k1 {k2 k3}}
  & h1 ~ $([<] $(k1 lt))
  & h2 ~ $([=] $(k2 eq))
  & lt ~ $([*] $(2 lt2))
  & lt2 ~ $([+] $(eq sel))
  & sel ~ ?((@gci_front @gci_more) (h3 (c (t (k3 o)))))
@gci_front = (h (c (t (k (1 ((k 1) (1 ((h c) t))))))))
@gci_more = (d (h (c (t (k o)))))
  & d ~ ?((@gci_eq @gci_after) (h (c (t (k o)))))
@gci_eq = (h (c (t (* (1 ((h c2) t))))))
  & c ~ $([+1] c2)
@gci_after = (* (h (c (t (k (1 ((h c) o2)))))))
  & @gci ~ (t (k o2))
"""

MAJ = """
@gmaj = ((tag pl) (bv (bc o)))
  & tag ~ ?((@gmaj_nil @gmaj_cons) (pl (bv (bc o))))
@gmaj_nil = (* (bv (* bv)))
@gmaj_cons = (* (((v c) t) (bv (bc o))))
  & c ~ {c1 c2}
  & bc ~ {bc1 bc2}
  & c1 ~ $([>] $(bc1 gt))
  & gt ~ ?((@gmaj_keep @gmaj_take) (v (c2 (bv (bc2 (t o))))))
@gmaj_keep = (* (* (bv (bc (t o)))))
  & @gmaj ~ (t (bv (bc o)))
@gmaj_take = (* (v (c (* (* (t o))))))
  & @gmaj ~ (t (v (c o)))
"""


def numeric_copies(b, k):
    """@gv{k} ~ (T (L (V1 (V2 ... Vk)))): k numeric tries whose leaf i is the label x of state leaf (x (sz ch));
    sz and the channel lists are erased."""
    outs = " ".join(f"(o{j}" for j in range(1, k)) + f" o{k}" + ")" * (k - 1)
    outs_a = " ".join(f"(a{j}" for j in range(1, k)) + f" a{k}" + ")" * (k - 1)
    outs_c = " ".join(f"(c{j}" for j in range(1, k)) + f" c{k}" + ")" * (k - 1)
    node_o = " ".join(f"((a{j} c{j})" for j in range(1, k)) + f" (a{k} c{k})" + ")" * (k - 1)
    dup = "x"
    for j in range(k, 1, -1):
        dup = f"{{o{j - 1} {dup}}}" if j == k else f"{{o{j - 1} {dup}}}"
    # build {o1 {o2 ... {o(k-1) ok}}}
    d = f"o{k}"
    for j in range(k - 1, 0, -1): d = f"{{o{j} {d}}}"
    b.add(f"""
@gv{k} = (t (L o))
  & L ~ ?((@gv{k}_leaf @gv{k}_node) (t o))
@gv{k}_leaf = ((x *) {outs})
  & x ~ {d}
@gv{k}_node = (lm ((ta tc) {node_o}))
  & lm ~ {{l1 l2}}
  & @gv{k} ~ (ta (l1 {outs_a}))
  & @gv{k} ~ (tc (l2 {outs_c}))
""")
    return f"gv{k}"


def edge_rewrite(b):
    """@gedge ~ (L (V (es E))): rewrite the edge list es through the canonical-id trie V (numeric leaves, depth L):
    (a, b) -> (min(V[a], V[b]), max(...)), self loops dropped, duplicates collapsed, output sorted lexicographically.
    Lookups V[a], V[b] are multicast requests (reply wires registered while the edge list streams; delivered in O(L)
    once V exists). Each rewritten pair is pushed into bucket x (trie keyed by x) with a sorted, dedup insert (set
    semantics), and self loops are dropped by the act (the flag rides in the payload). A fold emits the buckets in
    key order."""
    lg(b)
    const_trie(b, "gl_zl", "(0 *)")
    const_trie(b, "gl_zq", "(y y)")
    update(b, "gmq", "reply")
    from genome.lib.graphprims import mc_deliver
    mc_deliver(b, "gmd")
    b.add(SORTED_INSERT_DEDUP)
    update(b, "gebk", """(lst ((ne y) o))
  & ne ~ ?((@gebk_drop @gebk_go) (lst (y o)))""")
    b.add("""
@gebk_drop = (lst (* lst))
@gebk_go = (* (lst (y o)))
  & @gsd ~ (lst (y o))
@gpe = ((tag pl) (i (acc o)))
  & tag ~ ?((@gpe_nil @gpe_cons) (pl (i (acc o))))
@gpe_nil = (* (* (a a)))
@gpe_cons = (* ((y t) (i (acc (1 ((i1 y) o2))))))
  & i ~ {i1 i2}
  & @gpe ~ (t (i2 (acc o2)))
""")
    stream(b, "ge", 16, """((L (Q H)) ((a b) (L5 (Q2 H2))))
  & L ~ {L1 {L2 {L3 L5}}}
  & @gmq ~ (Q (a (L1 (ra Q1))))
  & @gmq ~ (Q1 (b (L2 (rb Q2))))
  & ra ~ {ra1 {ra2 ra3}}
  & rb ~ {rb1 {rb2 {rb3 rb4}}}
  & ra1 ~ $([<] $(rb1 lt))
  & ra2 ~ $([-] $(rb2 dab))
  & lt ~ $([*] $(dab p1))
  & rb3 ~ $([+] $(p1 x))
  & ra3 ~ $([+] $(rb4 sm))
  & x ~ {x1 {x2 x3}}
  & sm ~ $([-] $(x1 y))
  & y ~ {y1 y2}
  & x2 ~ $([!] $(y1 ne))
  & @gebk ~ (H (x3 (L3 ((ne y2) H2))))""", "((* (q h)) (q h))")
    fold(b, "geo", """(lst (i (acc o)))
  & @gpe ~ (lst (i (acc o)))""", idx=True, env=False)
    b.add("""
@gedge = (L (V (es E)))
  & L ~ {L1 {L2 {L3 {L4 L5}}}}
  & @gl_zq ~ (L1 Q0)
  & @gl_zl ~ (L2 H0)
  & @ge_blk ~ (es ((L3 (Q0 H0)) (Q H)))
  & @gmd ~ (V (Q L4))
  & @geo ~ (H (L5 (0 ((0 *) E))))
""")
    return "gedge"


def prop_merge(b):
    """@gprop ~ (L (V (at P))): merged attribute table. For each attribute (x, k, val) the cluster id V[x] is a
    multicast request; the value is count-inserted into bucket (V[x] << 2) | k of a trie of depth L + 2 (bucket =
    ascending list of (value, count)). A fold emits, in key order, (cid, key, majority) for every non-empty bucket;
    the majority is a scan keeping the first strictly larger count (ascending values -> ties go to the smallest)."""
    lg(b)
    const_trie(b, "gl_zl", "(0 *)")
    const_trie(b, "gl_zq", "(y y)")
    update(b, "gmq", "reply")
    from genome.lib.graphprims import mc_deliver
    mc_deliver(b, "gmd")
    b.add(COUNT_INSERT + MAJ)
    update(b, "gabk", "(lst (v o))\n  & @gci ~ (lst (v o))")
    stream(b, "ga", 16, """((L (Q H)) ((x (k v)) (L4 (Q2 H2))))
  & L ~ {L1 {L2 L4}}
  & @gmq ~ (Q (x (L1 (r Q2))))
  & r ~ $([<<] $(2 rs))
  & rs ~ $([|] $(k key))
  & L2 ~ $([+] $(2 L2p))
  & @gabk ~ (H (key (L2p (v H2))))""", "((* (q h)) (q h))")
    b.add("""
@gpo_nil = (* (* (a a)))
@gpo_cons = (* (pl (i (acc (1 ((c (k mv)) acc))))))
  & i ~ {i1 i2}
  & i1 ~ $([>>] $(2 c))
  & i2 ~ $([&] $(3 k))
  & @gmaj ~ ((1 pl) (16777215 (0 mv)))
""")
    fold(b, "gpo", """((tag pl) (i (acc o)))
  & tag ~ ?((@gpo_nil @gpo_cons) (pl (i (acc o))))""", idx=True, env=False)
    b.add("""
@gprop = (L (V (at P)))
  & L ~ {L1 {L2 {L3 L4}}}
  & L2 ~ $([+] $(2 L2p))
  & L2p ~ {La Lb}
  & @gl_zq ~ (L1 Q0)
  & @gl_zl ~ (La H0)
  & @ga_blk ~ (at ((L3 (Q0 H0)) (Q H)))
  & @gmd ~ (V (Q L4))
  & @gpo ~ (H (Lb (0 ((0 *) P))))
""")
    return "gprop"


def list_to_trie(b):
    """@gl2t ~ (c (Vo n)): n = len(c) and Vo = trie of depth lg(n-1) with leaf i = c[i] (0 beyond n); for n = 0,
    Vo = 0. The list is copied by a DUP (it is closed data): one copy is counted, the other is written by keyed
    `set` updates (keys = positions, known at once; they wait only for L)."""
    lg(b)
    const_trie(b, "gl_z0", "0")
    update(b, "gset", "set")
    stream(b, "gln", 16, "(n (* m))\n  & n ~ $([+1] m)", "(n n)")
    stream(b, "gcb", 16, """((i (L T)) (ci (ip (L2 T2))))
  & i ~ {i1 i2}
  & i2 ~ $([+1] ip)
  & L ~ {L1 L2}
  & @gset ~ (T (i1 (L1 (ci T2))))""", "((* (* T)) T)")
    return "gl2t"


def greedy_core2(b):
    """v2 of greedy_core, same ports: @gr ~ (L (tau (cap (mnl (cs (Tf h)))))).

    Pipelining by one step of label lookahead. Round k carries the PENDING decision D_{k-1} = (lo', hi', S) of the
    previous candidate instead of applying it in a separate phase:
      - A_k, sA_k = relabel(CU[u_k], D_{k-1}) and B_k likewise (a 3-round scalar relabel at the root; CU, CV are the
        numeric copies of the labels BEFORE step k-1, read by pre-expanded gets);
      - one traversal broadcasts D_{k-1} and (A_k, B_k); each leaf first relabels itself by D_{k-1} (x in {lo', hi'}
        -> (hi', S)), then does the conflict test for candidate k on the new labels: it sends x on every MNL channel,
        receives y, and ORs isA*(y == B) | isB*(y == A) (both compares in parallel); flags are OR-reduced;
      - @gdec2 turns (A, B, sizes, cap, c) into D_k by switches: A == B short-circuits to the no-op decision
        (BIG, BIG, 0) without waiting for the conflict reduction; otherwise bad = c | (sA + sB > cap) selects
        (min, max, sA + sB) or the no-op.
    So the critical path per candidate is ~ broadcast (L) + leaf (~5) + OR-reduce (L) + decision (~3), and a
    same-cluster candidate costs ~6. A final traversal applies D_m. Work per candidate O(2^L + |mnl|)."""
    sort_scores(b)
    get(b, "gget")
    mk_trie(b, "gmkT", "(b (b (1 (0 *))))")
    mk_trie(b, "gmkC", "(b (b 1))")
    update(b, "gpc", "((x (sz lst)) (P (x (sz (1 (P lst))))))")
    stream(b, "gm", 16, """((L T) ((a b) (L3 T2)))
  & L ~ {L1 {L2 L3}}
  & @gpc ~ (T (a (L1 ((c2 c1) T1))))
  & @gpc ~ (T1 (b (L2 ((c1 c2) T2))))""", "((* T) T)")
    same = "(* " * 9 + f"({BIG} ({BIG} (0 0)))" + ")" * 9
    b.add(f"""
@gr = (L (tau (cap (mnl (cs (Tf h))))))
  & L ~ {{L1 {{L2 {{L3 {{L4 {{L5 L6}}}}}}}}}}
  & @gmkT ~ (L1 (0 T0))
  & @gmkC ~ (L2 (0 CU0))
  & @gmkC ~ (L3 (0 CV0))
  & @gm_blk ~ (mnl ((L4 T0) T1))
  & @gl_zl ~ (10 Z)
  & @gs_blk ~ (cs (((L5 tau) Z) C))
  & @gsw ~ (C (10 ((T1 (CU0 (CV0 (L6 (cap (h ({BIG} ({BIG} 0)))))))) Sf)))
  & @gfin ~ (Sf Tf)
@gfin = ((T (* (* (L (* ((0 *) (lo (hi S)))))))) Tf)
  & @grd ~ (T (L (lo (hi (S ({BIG} ({BIG} (* (Tf (* *))))))))))
@gsw = (t (L (S So)))
  & L ~ ?((@gsw_leaf @gsw_node) (t (S So)))
@gsw_leaf = (lst (S So))
  & @gwl ~ (lst (S So))
@gsw_node = (lm ((a c) (S So)))
  & lm ~ {{l1 l2}}
  & @gsw ~ (a (l1 (S mid)))
  & @gsw ~ (c (l2 (mid So)))
@gwl = ((?((@gwl_nil @gwl_cons) (pl (S So))) pl) (S So))
@gwl_nil = (* (S S))
@gwl_cons = (* ((h t) (S So)))
  & @gst ~ (S (h S2))
  & @gwl ~ (t (S2 So))
// one round: candidate pk = (u << L) | v, pending decision (lo hi S) of the previous candidate
@gst = ((T (CU (CV (L (cap (h (lo (hi S)))))))) (pk (T2 (CU2 (CV2 (L6 (cap2 (h2 (lo2 (hi2 S2))))))))))
  & L ~ {{L1 {{L2 {{L3 {{L4 {{L5 L6}}}}}}}}}}
  & cap ~ {{cp1 cap2}}
  & pk ~ {{pk1 pk2}}
  & pk1 ~ $([>>] $(L1 u))
  & 1 ~ $([<<] $(L2 m1))
  & m1 ~ $([-] $(1 msk))
  & pk2 ~ $([&] $(msk v))
  & u ~ {{u1 u2}}
  & v ~ {{v1 v2}}
  & lo ~ {{loa {{lob loc}}}}
  & hi ~ {{hia {{hib hic}}}}
  & S ~ {{Sa {{Sb Sc}}}}
  & @gget ~ (CU (u1 (L3 oA)))
  & @gget ~ (CV (v1 (L4 oB)))
  & @grl1 ~ (oA (loa (hia (Sa (A sA)))))
  & @grl1 ~ (oB (lob (hib (Sb (B sB)))))
  & A ~ {{A1 A2}}
  & B ~ {{B1 B2}}
  & @grd ~ (T (L5 (loc (hic (Sc (A1 (B1 (c (T2 (CU2 CV2))))))))))
  & @gdec ~ ((A2 (B2 (sA (sB (cp1 c))))) (lo2 (hi2 (S2 sk))))
  & sk ~ ?((@gst_keep @gst_skip) (h (h2 (u2 v2))))
@gst_keep = (h (h (* *)))
@gst_skip = (* ((1 ((u v) h2)) (h2 (u v))))
// scalar relabel of (x sz) by a decision: x in {{lo, hi}} -> (hi, S)
@grl1 = ((x sz) (lo (hi (S o))))
  & x ~ {{x1 {{x2 x3}}}}
  & hi ~ {{hi1 hi2}}
  & x1 ~ $([=] $(lo e1))
  & x2 ~ $([=] $(hi1 e2))
  & e1 ~ $([|] $(e2 m))
  & m ~ ?((@grl1_keep @grl1_take) (x3 (sz (hi2 (S o)))))
@grl1_keep = (x (sz (* (* (x sz)))))
@grl1_take = (* (* (* (hi (S (hi S))))))
// decision
@gdec = ((A (B (sA (sB (cap c))))) (lo2 (hi2 (S sk))))
  & A ~ {{Aa {{Ab Ac}}}}
  & B ~ {{Ba {{Bb Bc}}}}
  & Aa ~ $([=] $(Ba same))
  & same ~ ?((@gdec_diff @gdec_same) (Ab (Bb (Ac (Bc (sA (sB (cap (c (lo2 (hi2 (S sk))))))))))))
@gdec_same = {same}
@gdec_diff = (Ab (Bb (Ac (Bc (sA (sB (cap (c (lo2 (hi2 (S sk)))))))))))
  & Ab ~ $([<] $(Bb lt))
  & lt ~ ?((@gdec_ge @gdec_lt) (Ac (Bc (lo hi))))
  & sA ~ $([+] $(sB ssum))
  & ssum ~ {{S0 s2}}
  & cap ~ $([<] $(s2 capf))
  & c ~ $([|] $(capf bad))
  & bad ~ {{bad1 sk}}
  & bad1 ~ ?((@gdec_ok @gdec_bad) (lo (hi (S0 (lo2 (hi2 S))))))
@gdec_ok = (lo (hi (S (lo (hi S)))))
@gdec_bad = (* (* (* (* ({BIG} ({BIG} 0))))))
@gdec_ge = (a (b (b a)))
@gdec_lt = (* (a (b (a b))))
// traversal: relabel by (lo hi S), then conflict test for (A, B) on the new labels; numeric copies for the gets
@grd = (T (L (lo (hi (S (A (B (c (T2 (CU CV))))))))))
  & L ~ ?((@grd_leaf @grd_node) (T (lo (hi (S (A (B (c (T2 (CU CV))))))))))
@grd_node = (lm ((ta tb) (lo (hi (S (A (B (c ((a2 b2) ((ua ub) (va vb)))))))))))
  & lm ~ {{l1 l2}}
  & A ~ {{A1 A2}}
  & B ~ {{B1 B2}}
  & lo ~ {{lo1 lo2}}
  & hi ~ {{hi1 hi2}}
  & S ~ {{S1 S2}}
  & @grd ~ (ta (l1 (lo1 (hi1 (S1 (A1 (B1 (c1 (a2 (ua va))))))))))
  & @grd ~ (tb (l2 (lo2 (hi2 (S2 (A2 (B2 (c2 (b2 (ub vb))))))))))
  & c1 ~ $([|] $(c2 c))
@grd_leaf = ((x (sz ch)) (lo (hi (S (A (B (c ((x2 (sz2 ch2)) ((cux cus) (cvx cvs))))))))))
  & @grl1 ~ ((x sz) (lo (hi (S (xn szn)))))
  & xn ~ {{cux {{cvx {{xc x2}}}}}}
  & szn ~ {{cus {{cvs sz2}}}}
  & xc ~ {{xa {{xb xs}}}}
  & A ~ {{Aa Ab}}
  & B ~ {{Ba Bb}}
  & xa ~ $([=] $(Aa isA))
  & xb ~ $([=] $(Ba isB))
  & @gcw ~ (ch (xs (isA (isB (Ab (Bb (c ch2)))))))
@gcw = ((?((@gcw_nil @gcw_cons) (pl C)) pl) C)
@gcw_nil = (* (* (* (* (* (* (0 (0 *))))))))
@gcw_cons = (* (((i o) rest) (x (iA (iB (A (B (c (1 ((i2 o2) rest2))))))))))
  & x ~ {{x1 x2}}
  & iA ~ {{iA1 iA2}}
  & iB ~ {{iB1 iB2}}
  & A ~ {{A1 A2}}
  & B ~ {{B1 B2}}
  & o ~ (x1 o2)
  & i ~ (y i2)
  & y ~ {{y1 y2}}
  & y1 ~ $([=] $(B1 eB))
  & y2 ~ $([=] $(A1 eA))
  & eB ~ $([*] $(iA1 p))
  & eA ~ $([*] $(iB1 q))
  & p ~ $([|] $(q r))
  & r ~ $([|] $(c2 c))
  & @gcw ~ (rest (x2 (iA2 (iB2 (A2 (B2 (c2 rest2)))))))
""")
    return "gr"


def greedy_core3(b):
    """v3 of greedy_core, same ports: @gr ~ (L (tau (cap (mnl (cs (Tf h)))))). Tf leaves are (x sz).

    Two tries instead of one:
      - the node trie T (depth L, leaf (x sz)) is only relabelled; it is OFF the critical path: round k applies the
        pending decision D_{k-1} to it and emits numeric copies for the next rounds' gets;
      - the MNL trie M (depth LM = lg|mnl|, leaf (la lb) = current labels of the two ends of must-not-link pair i;
        unused leaves (BIG BIG)) is where the conflict test runs: round k broadcasts D_{k-1} and (A_k, B_k) down M,
        each leaf relabels its ends (x == lo -> hi) and tests {la, lb} == {A, B}; flags are OR-reduced up M.
    The critical path per candidate is D_{k-1} -> A_k (scalar relabel of the copy value, ~5 rounds) -> broadcast
    down M (LM) -> leaf (~6) -> OR-reduce (2 LM) -> decision (~3, inline switches with shallow contexts; a same-
    cluster or over-cap merge is resolved before the reduction arrives). Without MNL pairs LM = 0.
    Lessons from v2 (measured): switch branches that are REF definitions with deep contexts cost one round per
    nesting level of the context, so on the per-step chain use inline branch patterns with the output first."""
    sort_scores(b)
    get(b, "gget")
    lg(b)
    mk_trie(b, "gmkC", "(b (b 1))")
    const_trie(b, "gl_zp", f"({BIG} {BIG})")
    update(b, "gms", "set")
    stream(b, "gln", 16, "(n (* m))\n  & n ~ $([+1] m)", "(n n)")
    stream(b, "gmb", 16, """((i (L T)) (ab (ip (L2 T2))))
  & i ~ {i1 i2}
  & i2 ~ $([+1] ip)
  & L ~ {L1 L2}
  & @gms ~ (T (i1 (L1 (ab T2))))""", "((* (* T)) T)")
    b.add(f"""
@gr = (L (tau (cap (mnl (cs (Tf h))))))
  & L ~ {{L1 {{L2 {{L3 {{L5 L6}}}}}}}}
  & @gmkC ~ (L1 (0 T0))
  & @gmkC ~ (L2 (0 CU0))
  & @gmkC ~ (L3 (0 CV0))
  & mnl ~ {{mn1 mn2}}
  & @gln_blk ~ (mn1 (0 M))
  & @lg ~ (M LM)
  & LM ~ {{LMa {{LMb LMc}}}}
  & @gl_zp ~ (LMa Mt0)
  & @gmb_blk ~ (mn2 ((0 (LMb Mt0)) Mt))
  & @gl_zl ~ (10 Z)
  & @gs_blk ~ (cs (((L5 tau) Z) C))
  & @gsw ~ (C (10 ((T0 (CU0 (CV0 (Mt (L6 (LMc (cap (h (16777215 (16777215 0)))))))))) Sf)))
  & @gfin ~ (Sf Tf)
@gfin = ((T (* (* (* (L (* (* ((0 *) (lo (hi S)))))))))) Tf)
  & @gnt ~ (T (L (lo (hi (S (Tf (* *)))))))
@gsw = (t (L (S So)))
  & L ~ ?((@gsw_leaf @gsw_node) (t (S So)))
@gsw_leaf = (lst (S So))
  & @gwl ~ (lst (S So))
@gsw_node = (lm ((a c) (S So)))
  & lm ~ {{l1 l2}}
  & @gsw ~ (a (l1 (S mid)))
  & @gsw ~ (c (l2 (mid So)))
@gwl = ((?((@gwl_nil @gwl_cons) (pl (S So))) pl) (S So))
@gwl_nil = (* (S S))
@gwl_cons = (* ((h t) (S So)))
  & @gst ~ (S (h S2))
  & @gwl ~ (t (S2 So))
// one round: candidate pk = (u << L) | v; pending decision (lo hi S) of the previous candidate
@gst = ((T (CU (CV (Mt (L (LM (cap (h (lo (hi S)))))))))) (pk (T2 (CU2 (CV2 (Mt2 (Lo (LMo (cap2 (h2 (lo2 (hi2 S2))))))))))))
  & L ~ {{L1 {{L2 {{L3 {{L4 {{L5 Lo}}}}}}}}}}
  & LM ~ {{LM1 LMo}}
  & cap ~ {{cp1 cap2}}
  & pk ~ {{pk1 pk2}}
  & pk1 ~ $([>>] $(L1 u))
  & 1 ~ $([<<] $(L2 m1))
  & m1 ~ $([-] $(1 msk))
  & pk2 ~ $([&] $(msk v))
  & u ~ {{u1 u2}}
  & v ~ {{v1 v2}}
  & lo ~ {{lod {{loa {{lob loc}}}}}}
  & hi ~ {{hid {{hia {{hib hic}}}}}}
  & S ~ {{Sa {{Sb Sc}}}}
  & @gget ~ (CU (u1 (L3 oA)))
  & @gget ~ (CV (v1 (L4 oB)))
  & @grs ~ (oA (loa (hia (Sa (A sA)))))
  & @grs ~ (oB (lob (hib (Sb (B sB)))))
  & A ~ {{A1 A2}}
  & B ~ {{B1 B2}}
  & @gmt ~ (Mt (LM1 (lod (hid (A1 (B1 (c Mt2)))))))
  & @gnt ~ (T (L5 (loc (hic (Sc (T2 (CU2 CV2)))))))
  & @gdec ~ ((A2 (B2 (sA (sB (cp1 c))))) (lo2 (hi2 (S2 sk))))
  & sk ~ ?((@gst_keep @gst_skip) (h (h2 (u2 v2))))
@gst_keep = (h (h (* *)))
@gst_skip = (* ((1 ((u v) h2)) (h2 (u v))))
// label relabel: o = (x == lo) ? hi : x
@grx = (x (lo (hi o)))
  & x ~ {{x1 x2}}
  & x1 ~ $([=] $(lo e))
  & e ~ ?(((a (* a)) (* (* (b b)))) (x2 (hi o)))
// relabel of (x sz): x by @grx, sz := S if x in {{lo, hi}}
@grs = ((x sz) (lo (hi (S (A sA)))))
  & x ~ {{x1 {{x2 x3}}}}
  & lo ~ {{lo1 lo2}}
  & hi ~ {{hi1 hi2}}
  & @grx ~ (x1 (lo1 (hi1 A)))
  & x2 ~ $([=] $(lo2 e1))
  & x3 ~ $([=] $(hi2 e2))
  & e1 ~ $([|] $(e2 m))
  & m ~ ?(((p (* p)) (* (* (q q)))) (sz (S sA)))
// decision
@gdec = ((A (B (sA (sB (cap c))))) (lo2 (hi2 (S sk))))
  & A ~ {{Aa {{Ab Ac}}}}
  & B ~ {{Ba {{Bb Bc}}}}
  & Aa ~ $([=] $(Ba same))
  & Ab ~ $([<] $(Bb lt))
  & lt ~ ?(((p1 (q1 (q1 p1))) (* (p2 (q2 (p2 q2))))) (Ac (Bc (lo hi))))
  & sA ~ $([+] $(sB ssum))
  & ssum ~ {{S s2}}
  & cap ~ $([<] $(s2 capf))
  & capf ~ {{cf1 cf2}}
  & same ~ {{sm1 sm2}}
  & sm1 ~ $([|] $(cf1 pre))
  & pre ~ ?(((a1 (b1 (a1 b1))) (* (* (* ({BIG} {BIG}))))) (lo (hi (Glo Ghi))))
  & c ~ {{c1 c2}}
  & c1 ~ ?((((a3 b3) (a3 b3)) (* (({BIG} {BIG}) (* *)))) ((lo2 hi2) (Glo Ghi)))
  & c2 ~ $([|] $(cf2 bad))
  & sm2 ~ $([=] $(0 ns))
  & ns ~ $([*] $(bad sk))
// node trie: relabel only, plus two numeric copies
@gnt = (T (L (lo (hi (S (T2 (CU CV)))))))
  & L ~ ?((@gnt_leaf @gnt_node) (T (lo (hi (S (T2 (CU CV)))))))
@gnt_node = (lm ((ta tb) (lo (hi (S ((a2 b2) ((ua ub) (va vb))))))))
  & lm ~ {{l1 l2}}
  & lo ~ {{lo1 lo2}}
  & hi ~ {{hi1 hi2}}
  & S ~ {{S1 S2}}
  & @gnt ~ (ta (l1 (lo1 (hi1 (S1 (a2 (ua va)))))))
  & @gnt ~ (tb (l2 (lo2 (hi2 (S2 (b2 (ub vb)))))))
@gnt_leaf = (xs (lo (hi (S ((x2 s2) ((xu su) (xv sv)))))))
  & @grs ~ (xs (lo (hi (S (xn sn)))))
  & xn ~ {{xu {{xv x2}}}}
  & sn ~ {{su {{sv s2}}}}
// MNL trie: relabel the pair's ends, then test {{la, lb}} == {{A, B}}; OR-reduce
@gmt = (M (L (lo (hi (A (B (c M2)))))))
  & L ~ ?((@gmt_leaf @gmt_node) (M (lo (hi (A (B (c M2)))))))
@gmt_node = (lm ((ma mb) (lo (hi (A (B (c (a2 b2))))))))
  & lm ~ {{l1 l2}}
  & lo ~ {{lo1 lo2}}
  & hi ~ {{hi1 hi2}}
  & A ~ {{A1 A2}}
  & B ~ {{B1 B2}}
  & @gmt ~ (ma (l1 (lo1 (hi1 (A1 (B1 (c1 a2)))))))
  & @gmt ~ (mb (l2 (lo2 (hi2 (A2 (B2 (c2 b2)))))))
  & c1 ~ $([|] $(c2 c))
@gmt_leaf = ((la lb) (lo (hi (A (B (c (la2 lb2)))))))
  & lo ~ {{o1 o2}}
  & hi ~ {{h1 h2}}
  & @grx ~ (la (o1 (h1 xa)))
  & @grx ~ (lb (o2 (h2 xb)))
  & xa ~ {{la2 {{xa1 xa2}}}}
  & xb ~ {{lb2 {{xb1 xb2}}}}
  & A ~ {{A1 A2}}
  & B ~ {{B1 B2}}
  & xa1 ~ $([=] $(A1 e1))
  & xb1 ~ $([=] $(B1 e2))
  & xa2 ~ $([=] $(B2 e3))
  & xb2 ~ $([=] $(A2 e4))
  & e1 ~ $([&] $(e2 f1))
  & e3 ~ $([&] $(e4 f2))
  & f1 ~ $([|] $(f2 c))
""")
    return "gr"


def greedy_core4(b):
    """v4 = v3 with the scalar relabel of the candidate's ends moved into the MNL leaves: the pending decision
    D_{k-1} and the UNrelabelled end labels (oA, oB, read before D_{k-1} is known) are broadcast down the MNL trie
    at once, and every leaf relabels la, lb, oA, oB in parallel before comparing. This takes the root's
    relabel-then-broadcast off the per-candidate chain (the root still relabels A, B for the decision, in parallel).
    Same ports as greedy_core."""
    t = Book()
    greedy_core3(t)
    txt = t.text()
    txt = txt.replace("""  & @gget ~ (CU (u1 (L3 oA)))
  & @gget ~ (CV (v1 (L4 oB)))
  & @grs ~ (oA (loa (hia (Sa (A sA)))))
  & @grs ~ (oB (lob (hib (Sb (B sB)))))
  & A ~ {A1 A2}
  & B ~ {B1 B2}
  & @gmt ~ (Mt (LM1 (lod (hid (A1 (B1 (c Mt2)))))))""", """  & @gget ~ (CU (u1 (L3 (ax as))))
  & @gget ~ (CV (v1 (L4 (bx bs))))
  & ax ~ {ax1 ax2}
  & bx ~ {bx1 bx2}
  & @grs ~ ((ax1 as) (loa (hia (Sa (A sA)))))
  & @grs ~ ((bx1 bs) (lob (hib (Sb (B sB)))))
  & @gmt ~ (Mt (LM1 (lod (hid (ax2 (bx2 (c Mt2)))))))""")
    txt = txt.replace("""  & @gdec ~ ((A2 (B2 (sA (sB (cp1 c))))) (lo2 (hi2 (S2 sk))))""",
                      """  & @gdec ~ ((A (B (sA (sB (cp1 c))))) (lo2 (hi2 (S2 sk))))""")
    old_leaf = txt[txt.index("@gmt_leaf = "):]
    old_leaf = old_leaf[:old_leaf.index("\n@", 1) + 1] if "\n@" in old_leaf[1:] else old_leaf
    new_leaf = """@gmt_leaf = ((la lb) (lo (hi (oa (ob (c (la2 lb2)))))))
  & lo ~ {o1 {o2 {o3 o4}}}
  & hi ~ {h1 {h2 {h3 h4}}}
  & @grx ~ (la (o1 (h1 xa)))
  & @grx ~ (lb (o2 (h2 xb)))
  & @grx ~ (oa (o3 (h3 A)))
  & @grx ~ (ob (o4 (h4 B)))
  & xa ~ {la2 {xa1 xa2}}
  & xb ~ {lb2 {xb1 xb2}}
  & A ~ {A1 A2}
  & B ~ {B1 B2}
  & xa1 ~ $([=] $(A1 e1))
  & xb1 ~ $([=] $(B1 e2))
  & xa2 ~ $([=] $(B2 e3))
  & xb2 ~ $([=] $(A2 e4))
  & e1 ~ $([&] $(e2 f1))
  & e3 ~ $([&] $(e4 f2))
  & f1 ~ $([|] $(f2 c))
"""
    txt = txt.replace(old_leaf, new_leaf)
    b.add(txt)
    return "gr"


def _nest(xs):
    t = xs[-1]
    for x in reversed(xs[:-1]): t = f"({x} {t})"
    return t


def greedy_core5(b):
    """v5: v3 plus speculation on the previous candidate's late bit. Same ports as greedy_core.

    A decision is split into an EARLY part E_k = (lo', hi', S) (the merge candidate k would do: min/max of its
    clusters, or the no-op (BIG, BIG) when same-cluster or over cap; known as soon as A_k, B_k are) and a LATE bit
    ok_k = no must-not-link conflict (known only after the OR-reduction). Round k knows E_{k-1} early but not ok_{k-1},
    so it evaluates candidate k under both hypotheses: the MNL leaves test {la, lb} == {A, B} on labels "after k-2"
    (hypothesis 0) and on those labels relabelled by E_{k-1} (hypothesis 1), packing the two flags as c0 + 2 c1 in one
    OR-reduction; the root then selects with ok_{k-1}, a 3-round switch. The node trie lags two candidates (round k
    applies D_{k-2} = ok_{k-2} ? E_{k-2} : no-op), and round k's end labels are read from its copies and relabelled at
    the root, so no trie traversal waits for ok_{k-1}. Final: D_{m-1} and D_m applied by two node traversals."""
    sort_scores(b)
    get(b, "gget")
    lg(b)
    mk_trie(b, "gmkC", "(b (b 1))")
    const_trie(b, "gl_zp", f"({BIG} {BIG})")
    update(b, "gms", "set")
    stream(b, "gln", 16, "(n (* m))\n  & n ~ $([+1] m)", "(n n)")
    stream(b, "gmb", 16, """((i (L T)) (ab (ip (L2 T2))))
  & i ~ {i1 i2}
  & i2 ~ $([+1] ip)
  & L ~ {L1 L2}
  & @gms ~ (T (i1 (L1 (ab T2))))""", "((* (* T)) T)")
    NOOP = f"({BIG} ({BIG} 0))"
    st = _nest("T CU CV Mt L LM cap h E2 ok2 E1 ok1".split())
    st2 = _nest("T2 CU2 CV2 Mt2 Lo LMo cap2 h2 E1b ok1b Ek okk".split())
    init = _nest(["T0", "CU0", "CV0", "Mt", "L6", "LMc", "cap", "h", NOOP, "0", NOOP, "0"])
    fin = _nest(["T", "*", "*", "*", "L", "*", "*", "(0 *)", "E2", "ok2", "E1", "ok1"])
    b.add(f"""
@gr = (L (tau (cap (mnl (cs (Tf h))))))
  & L ~ {{L1 {{L2 {{L3 {{L5 L6}}}}}}}}
  & @gmkC ~ (L1 (0 T0))
  & @gmkC ~ (L2 (0 CU0))
  & @gmkC ~ (L3 (0 CV0))
  & mnl ~ {{mn1 mn2}}
  & @gln_blk ~ (mn1 (0 M))
  & @lg ~ (M LM)
  & LM ~ {{LMa {{LMb LMc}}}}
  & @gl_zp ~ (LMa Mt0)
  & @gmb_blk ~ (mn2 ((0 (LMb Mt0)) Mt))
  & @gl_zl ~ (10 Z)
  & @gs_blk ~ (cs (((L5 tau) Z) C))
  & @gsw ~ (C (10 ({init} Sf)))
  & @gfin ~ (Sf Tf)
@gfin = ({fin} Tf)
  & L ~ {{La Lb}}
  & ok2 ~ ?(((* {NOOP}) (* (e e))) (E2 D2))
  & ok1 ~ ?(((* {NOOP}) (* (f f))) (E1 D1))
  & D2 ~ (a (b c))
  & D1 ~ (x (y z))
  & @gnt ~ (T (La (a (b (c (T1 (* *)))))))
  & @gnt ~ (T1 (Lb (x (y (z (Tf (* *)))))))
@gsw = (t (L (S So)))
  & L ~ ?((@gsw_leaf @gsw_node) (t (S So)))
@gsw_leaf = (lst (S So))
  & @gwl ~ (lst (S So))
@gsw_node = (lm ((a c) (S So)))
  & lm ~ {{l1 l2}}
  & @gsw ~ (a (l1 (S mid)))
  & @gsw ~ (c (l2 (mid So)))
@gwl = ((?((@gwl_nil @gwl_cons) (pl (S So))) pl) (S So))
@gwl_nil = (* (S S))
@gwl_cons = (* ((h t) (S So)))
  & @gst ~ (S (h S2))
  & @gwl ~ (t (S2 So))
// round k: E2/ok2 = decision k-2 (resolved), E1 = early part of k-1, ok1 = its late bit
@gst = ({st} (pk {st2}))
  & L ~ {{L1 {{L2 {{L3 {{L4 {{L5 Lo}}}}}}}}}}
  & LM ~ {{LM1 LMo}}
  & cap ~ {{cp1 cap2}}
  & pk ~ {{pk1 pk2}}
  & pk1 ~ $([>>] $(L1 u))
  & 1 ~ $([<<] $(L2 m1))
  & m1 ~ $([-] $(1 msk))
  & pk2 ~ $([&] $(msk v))
  & u ~ {{u1 u2}}
  & v ~ {{v1 v2}}
  & @gget ~ (CU (u1 (L3 oA3)))
  & @gget ~ (CV (v1 (L4 oB3)))
  & ok2 ~ ?(((* {NOOP}) (* (e e))) (E2 D2))
  & D2 ~ (dlo (dhi dS))
  & dlo ~ {{dl1 {{dl2 dl3}}}}
  & dhi ~ {{dh1 {{dh2 dh3}}}}
  & dS ~ {{dS1 {{dS2 dS3}}}}
  & @grs ~ (oA3 (dl1 (dh1 (dS1 (A0 sA0)))))
  & @grs ~ (oB3 (dl2 (dh2 (dS2 (B0 sB0)))))
  & @gnt ~ (T (L5 (dl3 (dh3 (dS3 (T2 (CU2 CV2)))))))
  & E1 ~ (elo (ehi eS))
  & elo ~ {{el1 {{el2 {{el3 el4}}}}}}
  & ehi ~ {{eh1 {{eh2 {{eh3 eh4}}}}}}
  & eS ~ {{eS1 {{eS2 eS3}}}}
  & E1b ~ (el4 (eh4 eS3))
  & A0 ~ {{A0x {{A0y A0z}}}}
  & B0 ~ {{B0x {{B0y B0z}}}}
  & sA0 ~ {{sA0x sA0y}}
  & sB0 ~ {{sB0x sB0y}}
  & @grs ~ ((A0x sA0x) (el1 (eh1 (eS1 PA1))))
  & @grs ~ ((B0x sB0x) (el2 (eh2 (eS2 PB1))))
  & ok1 ~ {{okA {{okC ok1b}}}}
  & @gmt ~ (Mt (LM1 (el3 (eh3 (okC (A0y (B0y (c Mt2))))))))
  & @gdec ~ ((okA ((A0z sA0y) (PA1 ((B0z sB0y) (PB1 (cp1 c)))))) (Ek (okk sk)))
  & sk ~ ?((@gst_keep @gst_skip) (h (h2 (u2 v2))))
@gst_keep = (h (h (* *)))
@gst_skip = (* ((1 ((u v) h2)) (h2 (u v))))
@grx = (x (lo (hi o)))
  & x ~ {{x1 x2}}
  & x1 ~ $([=] $(lo e))
  & e ~ ?(((a (* a)) (* (* (b b)))) (x2 (hi o)))
@grs = ((x sz) (lo (hi (S (A sA)))))
  & x ~ {{x1 {{x2 x3}}}}
  & lo ~ {{lo1 lo2}}
  & hi ~ {{hi1 hi2}}
  & @grx ~ (x1 (lo1 (hi1 A)))
  & x2 ~ $([=] $(lo2 e1))
  & x3 ~ $([=] $(hi2 e2))
  & e1 ~ $([|] $(e2 m))
  & m ~ ?(((p (* p)) (* (* (q q)))) (sz (S sA)))
// decision: select hypothesis by sel = ok_{{k-1}}; early part Ek, late bit okk = (no conflict)
@gdec = ((sel (PA0 (PA1 (PB0 (PB1 (cap c)))))) (Ek (okk sk)))
  & sel ~ {{s1 {{sq2 s3}}}}
  & s1 ~ ?(((p1 (* p1)) (* (* (q1 q1)))) (PA0 (PA1 PA)))
  & sq2 ~ ?(((p2 (* p2)) (* (* (q2 q2)))) (PB0 (PB1 PB)))
  & c ~ {{cx cy}}
  & cx ~ $([&] $(1 c0))
  & cy ~ $([>>] $(1 c1))
  & s3 ~ ?(((p3 (* p3)) (* (* (q3 q3)))) (c0 (c1 cb)))
  & PA ~ (A sA)
  & PB ~ (B sB)
  & A ~ {{Aa {{Ab Ac}}}}
  & B ~ {{Ba {{Bb Bc}}}}
  & Aa ~ $([=] $(Ba same))
  & Ab ~ $([<] $(Bb lt))
  & lt ~ ?(((p4 (q4 (q4 p4))) (* (p5 (q5 (p5 q5))))) (Ac (Bc (lo hi))))
  & sA ~ $([+] $(sB ssum))
  & ssum ~ {{S s2}}
  & cap ~ $([<] $(s2 capf))
  & capf ~ {{cf1 cf2}}
  & same ~ {{sm1 sm2}}
  & sm1 ~ $([|] $(cf1 pre))
  & pre ~ ?(((a1 (b1 (a1 b1))) (* (* (* ({BIG} {BIG}))))) (lo (hi (Glo Ghi))))
  & Ek ~ (Glo (Ghi S))
  & cb ~ {{cb1 cb2}}
  & cb1 ~ $([=] $(0 okk))
  & cb2 ~ $([|] $(cf2 bad))
  & sm2 ~ $([=] $(0 ns))
  & ns ~ $([*] $(bad sk))
@gnt = (T (L (lo (hi (S (T2 (CU CV)))))))
  & L ~ ?((@gnt_leaf @gnt_node) (T (lo (hi (S (T2 (CU CV)))))))
@gnt_node = (lm ((ta tb) (lo (hi (S ((a2 b2) ((ua ub) (va vb))))))))
  & lm ~ {{l1 l2}}
  & lo ~ {{lo1 lo2}}
  & hi ~ {{hi1 hi2}}
  & S ~ {{S1 S2}}
  & @gnt ~ (ta (l1 (lo1 (hi1 (S1 (a2 (ua va)))))))
  & @gnt ~ (tb (l2 (lo2 (hi2 (S2 (b2 (ub vb)))))))
@gnt_leaf = (xs (lo (hi (S ((x2 s2) ((xu su) (xv sv)))))))
  & @grs ~ (xs (lo (hi (S (xn sn)))))
  & xn ~ {{xu {{xv x2}}}}
  & sn ~ {{su {{sv s2}}}}
// {{x, y}} == {{a, b}}
@gtest = (x (y (a (b c))))
  & x ~ {{x1 x2}}
  & y ~ {{y1 y2}}
  & a ~ {{a1 a2}}
  & b ~ {{b1 b2}}
  & x1 ~ $([=] $(a1 e1))
  & y1 ~ $([=] $(b1 e2))
  & x2 ~ $([=] $(b2 e3))
  & y2 ~ $([=] $(a2 e4))
  & e1 ~ $([&] $(e2 f1))
  & e3 ~ $([&] $(e4 f2))
  & f1 ~ $([|] $(f2 c))
// MNL trie, both hypotheses for the previous candidate's merge E = (lo, hi); output labels after it (by ok)
@gmt = (M (L (lo (hi (ok (A (B (c M2))))))))
  & L ~ ?((@gmt_leaf @gmt_node) (M (lo (hi (ok (A (B (c M2))))))))
@gmt_node = (lm ((ma mb) (lo (hi (ok (A (B (c (a2 b2)))))))))
  & lm ~ {{l1 l2}}
  & lo ~ {{lo1 lo2}}
  & hi ~ {{hi1 hi2}}
  & ok ~ {{ok1 ok2}}
  & A ~ {{A1 A2}}
  & B ~ {{B1 B2}}
  & @gmt ~ (ma (l1 (lo1 (hi1 (ok1 (A1 (B1 (c1 a2))))))))
  & @gmt ~ (mb (l2 (lo2 (hi2 (ok2 (A2 (B2 (c2 b2))))))))
  & c1 ~ $([|] $(c2 c))
@gmt_leaf = ((la lb) (elo (ehi (ok (A0 (B0 (c (la2 lb2))))))))
  & elo ~ {{o1 {{o2 {{o3 o4}}}}}}
  & ehi ~ {{h1 {{h2 {{h3 h4}}}}}}
  & la ~ {{la0 {{la1 lak}}}}
  & lb ~ {{lb0 {{lb1 lbk}}}}
  & A0 ~ {{A0a A0b}}
  & B0 ~ {{B0a B0b}}
  & @grx ~ (la1 (o1 (h1 xa)))
  & @grx ~ (lb1 (o2 (h2 xb)))
  & @grx ~ (A0b (o3 (h3 A1)))
  & @grx ~ (B0b (o4 (h4 B1)))
  & xa ~ {{xa1 xak}}
  & xb ~ {{xb1 xbk}}
  & @gtest ~ (la0 (lb0 (A0a (B0a c0))))
  & @gtest ~ (xa1 (xb1 (A1 (B1 c1))))
  & c1 ~ $([*] $(2 c1d))
  & c0 ~ $([|] $(c1d c))
  & ok ~ ?(((P0 (* P0)) (* (* (P1 P1)))) ((lak lbk) ((xak xbk) (la2 lb2))))
""")
    return "gr"
