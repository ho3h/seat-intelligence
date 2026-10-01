"""Builds the RECON-SWING nets (runs/exp10) from hand-written HVM2 text plus the templates in lib_ext.py.
usage: python3 runs/exp10/build.py <prog|all> [outfile]"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from lib_ext import cc_core, cc_pipe, tl_leafmap, lib, INC, get, nav, stream  # noqa: E402
POP16 = open(os.path.join(os.path.dirname(D), "exp5", "tc.hvm.txt")).read()
POP16 = POP16[POP16.index("@pop16 = "):]
POP16 = POP16[:POP16.index("\n\n") + 1] if "\n\n" in POP16 else POP16

NETS = {}
ID = "  & y ~ x\n  & i ~ *"


def prog(name):
    def deco(f):
        NETS[name] = f
        return f
    return deco


# n = 0 guard + trie depth for (n es) inputs; body gets wires n, L, es, out
def pos_nes(zero_out, body, extra=""):
    return f"""@prog = ((n es) out)
  & n ~ ?((@pz @pp) (es out))
@pz = (* {zero_out})
@pp = (nm1 (es out))
  & nm1 ~ {{na nb}}
  & na ~ $([+1] n)
  & @lg ~ (nb L)
{body}
{extra}"""


@prog("t5_cluster_canon")
def _():
    return pos_nes("(0 *)", """  & L ~ {L1 L2}
  & @A_cc ~ (L1 (es Sf))
  & @A_tl ~ (Sf (L2 (0 (n ((0 *) out)))))""") + CORE("A", "mx", 0) + tl_leafmap("A", ID) + lib()


@prog("t5_cluster_label")
def _():
    return pos_nes("(0 *)", """  & L ~ {L1 L2}
  & @A_cc ~ (L1 (es Sf))
  & @A_tl ~ (Sf (L2 (0 (n ((0 *) out)))))""") + CORE("A", "mn", 16777215) + tl_leafmap("A", ID) + lib()


# count leaves i < n with x == i
CCN = """@ccn = (t (L (base (n o))))
  & L ~ ?((@ccn_leaf @ccn_node) (t (base (n o))))
@ccn_leaf = ((x *) (base (n o)))
  & base ~ {b1 b2}
  & x ~ $([=] $(b1 eq))
  & b2 ~ $([<] $(n inr))
  & eq ~ $([&] $(inr o))
@ccn_node = (lm ((a c) (base (n o))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {b1 b2}
  & n ~ {n1 n2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @ccn ~ (a (l1 (b1 (n1 x))))
  & @ccn ~ (c (l2 (bR (n2 y))))
  & x ~ $([+] $(y o))
"""


@prog("t5_cluster_count")
def _():
    return pos_nes("0", """  & L ~ {L1 L2}
  & @A_cc ~ (L1 (es Sf))
  & @ccn ~ (Sf (L2 (0 (n out))))""") + CORE("A", "mx", 0) + CCN + lib()



# ---------------------------------------------------------------- generic trie walkers
def ttl(name, leaf):
    """@{name} ~ (t (L (base (n (tail o))))): threads a list tail right-to-left through the leaves; `leaf` defines
    @{name}_leaf = (leafval (base (n (tail o))))."""
    return f"""@{name} = (t (L (base (n (tail o)))))
  & L ~ ?((@{name}_leaf @{name}_node) (t (base (n (tail o)))))
@{name}_node = (lm ((a b) (base (n (tail o)))))
  & lm ~ {{l1 {{l2 l3}}}}
  & base ~ {{b1 b2}}
  & n ~ {{n1 n2}}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @{name} ~ (a (l1 (b1 (n1 (mid o)))))
  & @{name} ~ (b (l2 (bR (n2 (tail mid)))))
{leaf}"""


def tred(name, leaf, op):
    """@{name} ~ (t (L (base (n o)))): reduce f(leaf, base, n) with operator op over all leaves."""
    return f"""@{name} = (t (L (base (n o))))
  & L ~ ?((@{name}_leaf @{name}_node) (t (base (n o))))
@{name}_node = (lm ((a c) (base (n o))))
  & lm ~ {{l1 {{l2 l3}}}}
  & base ~ {{b1 b2}}
  & n ~ {{n1 n2}}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @{name} ~ (a (l1 (b1 (n1 x))))
  & @{name} ~ (c (l2 (bR (n2 y))))
  & x ~ $([{op}] $(y o))
{leaf}"""


KEEP = "?(((* (t t)) (* (x (t2 (1 (x t2)))))) (y (tail o)))"   # keep ~ KEEP: prepend y to tail iff keep

# count trie from the final labels: Sf -> C (leaf c = size of the cluster whose label is c's index)
SCAT = """  & @zt ~ (Lz Z)
  & @scat ~ (Sf (Ls (Lss (Z C))))"""


def cnt_prog(zero_out, finish, extra, core="mx"):
    return pos_nes(zero_out, """  & L ~ {L1 {Lz {Ls {Lss L5}}}}
  & @A_cc ~ (L1 (es Sf))
""" + SCAT + "\n" + finish, extra) + CORE("A", core, 0) + INC + lib()


@prog("t5_cluster_sizes")
def _():
    return cnt_prog("(0 *)", "  & @szl ~ (C (L5 (0 (n ((0 *) out)))))", ttl("szl", """@szl_leaf = (c (base (n (tail o))))
  & c ~ {c1 y}
  & base ~ $([<] $(n inr))
  & c1 ~ $([>] $(0 pos))
  & pos ~ $([&] $(inr keep))
  & keep ~ """ + KEEP + "\n"))


@prog("t5_cluster_closure_pairs")
def _():
    return cnt_prog("0", "  & @pairs ~ (C (L5 out))\n  & n ~ *", PAIRS)


@prog("t5_cluster_largest")
def _():
    return cnt_prog("0", "  & @tmax ~ (C (L5 out))\n  & n ~ *", """@tmax = (t (L o))
  & L ~ ?((@tmax_leaf @tmax_node) (t o))
@tmax_leaf = (x x)
@tmax_node = (lm ((a b) o))
  & lm ~ {l1 l2}
  & @tmax ~ (a (l1 x))
  & @tmax ~ (b (l2 y))
  & @mx ~ (x (y o))
""")


PAIRS = """// pairs(t, L): sum over leaves of x*(x-1)/2
@pairs = (t (L o))
  & L ~ ?((@pairs_leaf @pairs_node) (t o))
@pairs_leaf = (x o)
  & x ~ {x1 x2}
  & x1 ~ $([-] $(1 y))
  & x2 ~ $([*] $(y z))
  & z ~ $([>>] $(1 o))
@pairs_node = (lm ((a b) o))
  & lm ~ {l1 l2}
  & @pairs ~ (a (l1 x))
  & @pairs ~ (b (l2 y))
  & x ~ $([+] $(y o))
"""

def nest(xs):
    t = xs[-1]
    for x in reversed(xs[:-1]): t = f"({x} {t})"
    return t
HIST8 = nest([f"h{j}" for j in range(1, 9)])
@prog("t5_cluster_histogram")
def _():
    z8 = "(1 (0 " * 8 + "(0 *)" + "))" * 8
    leaf = """@hg = (t (L (base (n o))))
  & L ~ ?((@hg_leaf @hg_node) (t (base (n o))))
@hg_node = (lm ((a c) (base (n """ + nest([f"g{j}" for j in range(1, 9)]) + """))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {b1 b2}
  & n ~ {n1 n2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @hg ~ (a (l1 (b1 (n1 """ + nest([f"x{j}" for j in range(1, 9)]) + """))))
  & @hg ~ (c (l2 (bR (n2 """ + nest([f"y{j}" for j in range(1, 9)]) + """))))
""" + "".join(f"  & x{j} ~ $([+] $(y{j} g{j}))\n" for j in range(1, 9)) + """@hg_leaf = (c (base (n """ + HIST8 + """)))
  & c ~ {c1 c2}
  & c1 ~ $([>] $(8 big))
  & big ~ ?(((q q) (* (* 8))) (c2 b))
  & base ~ $([<] $(n inr))
  & b ~ $([*] $(inr bb))
  & bb ~ {e1 {e2 {e3 {e4 {e5 {e6 {e7 e8}}}}}}}
""" + "".join(f"  & e{j} ~ $([=] $({j} h{j}))\n" for j in range(1, 9))
    out = "".join(f"(1 (h{j} " for j in range(1, 9)) + "(0 *)" + "))" * 8
    return cnt_prog(z8, "  & @hg ~ (C (L5 (0 (n " + HIST8 + "))))\n  & out ~ " + out, leaf)


@prog("t5_cluster_count_ge")
def _():
    return f"""@prog = ((n (k es)) out)
  & n ~ ?((@pz @pp) (k (es out)))
@pz = (* (* 0))
@pp = (nm1 (k (es out)))
  & nm1 ~ {{na nb}}
  & na ~ $([+1] n)
  & @lg ~ (nb L)
  & L ~ {{L1 {{Lz {{Ls {{Lss L5}}}}}}}}
  & @A_cc ~ (L1 (es Sf))
{SCAT}
  & k ~ $([<] $(1 k0))
  & k0 ~ ?(((q q) (* (* 1))) (k1 kk))
  & @cge ~ (C (L5 (0 (n (kk out)))))
@cge = (t (L (base (n (k o)))))
  & L ~ ?((@cge_leaf @cge_node) (t (base (n (k o)))))
@cge_node = (lm ((a c) (base (n (k o)))))
  & lm ~ {{l1 {{l2 l3}}}}
  & base ~ {{b1 b2}}
  & n ~ {{n1 n2}}
  & k ~ {{k1 k2}}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @cge ~ (a (l1 (b1 (n1 (k1 x)))))
  & @cge ~ (c (l2 (bR (n2 (k2 y)))))
  & x ~ $([+] $(y o))
@cge_leaf = (c (base (n (k o))))
  & base ~ $([<] $(n inr))
  & c ~ $([<] $(k lt))
  & lt ~ $([<] $(inr o))
""".replace("& k ~ $([<] $(1 k0))\n  & k0 ~ ?(((q q) (* (* 1))) (k1 kk))", "& k ~ {kA kB}\n  & kA ~ $([<] $(1 k0))\n  & k0 ~ ?(((q q) (* (* 1))) (kB kk))") + CORE("A", "mx", 0) + INC + lib()


@prog("t5_cluster_emit")
def _():
    return pos_nes("(0 *)", """  & L ~ {L1 L2}
  & @A_cc ~ (L1 (es Sf))
  & @em ~ (Sf (L2 (0 (n ((0 *) out)))))""", ttl("em", """@em_leaf = ((x *) (base (n (tail o))))
  & base ~ {b1 {b2 b3}}
  & x ~ {x1 x2}
  & b1 ~ $([<] $(n inr))
  & x1 ~ $([!] $(b2 ne))
  & ne ~ $([&] $(inr keep))
  & keep ~ ?(((* (t t)) (* (e (t2 (1 (e t2)))))) ((b3 x2) (tail o)))
""")) + CORE("A", "mx", 0) + lib()


@prog("t5_cluster_list")
def _():
    return pos_nes("(0 *)", """  & L ~ {L1 {L2 {L3 {L4 L5}}}}
  & n ~ {n1 n2}
  & @A_cc ~ (L1 (es Sf))
  & @zl ~ (L2 B0)
  & @bk ~ (Sf (L3 (L4 (0 (n1 (B0 B))))))
  & n2 ~ *
  & @lsl ~ (B (L5 ((0 *) out)))""", """// bk: push leaf index i (< n) onto bucket[label]; threaded right-to-left so buckets come out ascending
@bk = (S (L (LL (base (n (bi bo))))))
  & L ~ ?((@bk_leaf @bk_node) (S (LL (base (n (bi bo))))))
@bk_node = (lm ((a c) (LL (base (n (bi bo))))))
  & lm ~ {l1 {l2 l3}}
  & LL ~ {LA LB}
  & base ~ {b1 b2}
  & n ~ {n1 n2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @bk ~ (c (l2 (LB (bR (n2 (bi mid))))))
  & @bk ~ (a (l1 (LA (b1 (n1 (mid bo))))))
@bk_leaf = ((x *) (LL (base (n (bi bo)))))
  & base ~ {b1 b2}
  & b1 ~ $([<] $(n inr))
  & inr ~ ?((@bk_skip @bk_push) (x (LL (b2 (bi bo)))))
@bk_skip = (* (* (* (t t))))
@bk_push = (* (x (LL (i (t t2)))))
  & @pb ~ (t (x (LL (i t2))))
@pb_act = (lst (i (1 (i lst))))
// lsl: the non-empty buckets, in order
@lsl = (t (L (tail o)))
  & L ~ ?((@lsl_leaf @lsl_node) (t (tail o)))
@lsl_node = (lm ((a b) (tail o)))
  & lm ~ {l1 l2}
  & @lsl ~ (a (l1 (mid o)))
  & @lsl ~ (b (l2 (tail mid)))
@lsl_leaf = ((tg pl) (tail o))
  & tg ~ ?(((* (t t)) (* (p (t2 (1 ((1 p) t2)))))) (pl (tail o)))
""") + CORE("A", "mn", 16777215) + nav("pb", "pb_act") + lib()


def nx_prog(zero_out, finish, extra):
    """(n, x, pairs) inputs: n >= 1 always, but guard anyway."""
    return f"""@prog = ((n (x es)) out)
  & n ~ ?((@pz @pp) (x (es out)))
@pz = (* (* {zero_out}))
@pp = (nm1 (x (es out)))
  & nm1 ~ {{na nb}}
  & na ~ $([+1] n)
  & @lg ~ (nb L)
  & L ~ {{L1 {{L2 L3}}}}
  & @A_cc ~ (L1 (es Sf))
  & @A_get ~ (Sf (x (L2 (v S2))))
{finish}
{extra}""" + CORE("A", "mx", 0) + get("A") + lib()


@prog("t5_cluster_canon_of")
def _():
    return nx_prog("0", "  & v ~ out\n  & S2 ~ *\n  & L3 ~ *\n  & n ~ *", "")


@prog("t5_cluster_members_of")
def _():
    return nx_prog("(0 *)", "  & @mb ~ (S2 (L3 (0 (n (v ((0 *) out))))))", """@mb = (t (L (base (n (v (tail o))))))
  & L ~ ?((@mb_leaf @mb_node) (t (base (n (v (tail o))))))
@mb_node = (lm ((a b) (base (n (v (tail o))))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {b1 b2}
  & n ~ {n1 n2}
  & v ~ {v1 v2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @mb ~ (a (l1 (b1 (n1 (v1 (mid o))))))
  & @mb ~ (b (l2 (bR (n2 (v2 (tail mid))))))
@mb_leaf = ((lx *) (base (n (v (tail o)))))
  & base ~ {b1 y}
  & b1 ~ $([<] $(n inr))
  & lx ~ $([=] $(v eq))
  & eq ~ $([&] $(inr keep))
  & keep ~ """ + KEEP + "\n")


@prog("t5_cluster_same")
def _():
    return f"""@prog = ((n (es qs)) out)
  & n ~ ?((@pz @pp) (es (qs out)))
@pz = (* (* (0 *)))
@pp = (nm1 (es (qs out)))
  & nm1 ~ {{na nb}}
  & na ~ $([+1] n)
  & n ~ *
  & @lg ~ (nb L)
  & L ~ {{L1 L2}}
  & @A_cc ~ (L1 (es Sf))
  & @q_blk ~ (qs (((L2 (Sf out))) *))
@q_step = ((L (t h)) ((a b) (L3 (t2 h2))))
  & L ~ {{L1 {{L2 L3}}}}
  & @A_get ~ (t (a (L1 (va t1))))
  & @A_get ~ (t1 (b (L2 (vb t2))))
  & va ~ $([=] $(vb e))
  & h ~ (1 (e h2))
@q_fin = ((* (t (0 *))) t)
""".replace("(((L2 (Sf out))) *)", "((L2 (Sf out)) *)") + stream("q", 16, "q_step", "q_fin") + CORE("A", "mx", 0) + get("A") + lib()


def tau_prog(zero_out, finish, extra, core="mx"):
    return f"""@prog = ((n (tau es)) out)
  & n ~ ?((@pz @pp) (tau (es out)))
@pz = (* (* {zero_out}))
@pp = (nm1 (tau (es out)))
  & nm1 ~ {{na nb}}
  & na ~ $([+1] n)
  & @lg ~ (nb L)
  & L ~ {{L1 L2}}
  & @A_cct ~ (L1 (tau (es Sf)))
{finish}
{extra}""" + CORE("A", core, 0) + lib()


@prog("t5_reconcile_canon")
def _():
    return tau_prog("(0 *)", "  & @A_tl ~ (Sf (L2 (0 (n ((0 *) out)))))", tl_leafmap("A", ID))


@prog("t5_cluster_merge_count")
def _():
    return tau_prog("0", """  & n ~ {n1 n2}
  & @ccn ~ (Sf (L2 (0 (n1 c))))
  & n2 ~ $([-] $(c out))""", CCN)


# singletons: nodes that occur in no pair (no LP needed): n - |{endpoints}|
@prog("t5_cluster_singletons")
def _():
    return pos_nes("0", """  & L ~ {L1 L2}
  & @zt ~ (L1 T0)
  & @sg_blk ~ (es ((L2 T0) (L3 T)))
  & @cnt ~ (T (L3 c))
  & n ~ $([-] $(c out))""", """@sg_step = ((L t) ((u v) (L3 t2)))
  & L ~ {L1 {L2 L3}}
  & @ins ~ (t (u (L1 t1)))
  & @ins ~ (t1 (v (L2 t2)))
@sg_fin = ((L t) (L t))
""" + stream("sg", 16, "sg_step", "sg_fin")) + lib()


# implied_unproposed: sum s(s-1)/2 over clusters minus the number of distinct input pairs (bitset over u*2^L + v)
@prog("t5_cluster_implied_unproposed")
def _():
    return pos_nes("0", """  & L ~ {L1 {Lz {Ls {Lss {L5 {L6 {L7 L8}}}}}}}
  & n ~ *
  & @mk ~ (L1 (0 (1 S0)))
  & L6 ~ $([*] $(2 L2x))
  & L2x ~ {La Lb}
  & La ~ $([<] $(4 small))
  & small ~ ?(((q q) (* (* 4))) (Lb M))
  & M ~ $([-] $(4 DW))
  & DW ~ {DW1 {DW2 DW3}}
  & @zt ~ (DW1 W0)
  & @ip_blk ~ (es (((L7 DW2) (S0 W0)) (Sx W)))
  & @A_loop ~ (L8 (Sx Sf))
""" + SCAT + """
  & @pairs ~ (C (L5 cl))
  & @wpop ~ (W (DW3 dp))
  & cl ~ $([-] $(dp out))""", """@ip_step = (((L D) (s w)) ((u v) ((L4 D2) (s2 w2))))
  & L ~ {L1 {L2 {L3 L4}}}
  & D ~ {Da D2}
  & u ~ {u1 u2}
  & v ~ {v1 {v2 v3}}
  & @cp ~ (s (u1 (L1 ((c2 c1) s1))))
  & @cp ~ (s1 (v1 (L2 ((c1 c2) s2))))
  & u2 ~ $([<<] $(L3 uh))
  & uh ~ $([|] $(v2 key))
  & key ~ {k1 k2}
  & k1 ~ $([>>] $(4 kw))
  & k2 ~ $([&] $(15 kb))
  & 1 ~ $([<<] $(kb bit))
  & @sb ~ (w (kw (Da (bit w2))))
  & v3 ~ *
@ip_fin = ((* s) s)
@sb_act = (w (b o))
  & w ~ $([|] $(b o))
// wpop(t, D): total popcount of a word trie
@wpop = (t (L o))
  & L ~ ?((@wpop_leaf @wpop_node) (t o))
@wpop_leaf = (x o)
  & @pop16 ~ (x o)
@wpop_node = (lm ((a b) o))
  & lm ~ {l1 l2}
  & @wpop ~ (a (l1 x))
  & @wpop ~ (b (l2 y))
  & x ~ $([+] $(y o))
""" + POP16 + PAIRS + stream("ip", 16, "ip_step", "ip_fin") + nav("sb", "sb_act")) + CORE("A", "mx", 0) + INC + lib()

CORE = cc_pipe if os.environ.get("CORE", "pipe") == "pipe" else cc_core
if __name__ == "__main__":
    names = list(NETS) if sys.argv[1] == "all" else [sys.argv[1]]
    for nm in names:
        out = sys.argv[2] if len(sys.argv) > 2 and len(names) == 1 else os.path.join(D, nm + ".hvm")
        open(out, "w").write(NETS[nm]())
        print("wrote", out)
