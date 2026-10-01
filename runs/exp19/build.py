"""Builds the GRAPH-SWING-3 nets (runs/exp19) from per-program text (*.hvm.txt here), the exp5/exp9 templates and
runs/exp19/lib_ext.py.  usage: python runs/exp19/build.py <prog|all> [K]"""
import sys, os, importlib.util
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(D)
E5, E9 = os.path.join(R, "exp5"), os.path.join(R, "exp9")
sys.path.insert(0, E5); sys.path.insert(0, E9)
from lib import stream, nav
import lib_ext as X            # exp9 templates
_s = importlib.util.spec_from_file_location("lib_ext19", os.path.join(D, "lib_ext.py"))
Y = importlib.util.module_from_spec(_s); _s.loader.exec_module(Y)
_s = importlib.util.spec_from_file_location("build9", os.path.join(E9, "build.py"))
B9 = importlib.util.module_from_spec(_s); _s.loader.exec_module(B9)
r19 = lambda f: open(os.path.join(D, f)).read()
TRIE, SSSP, PEEL_BITS, ZL, TL = B9.TRIE, B9.SSSP, B9.PEEL_BITS, B9.ZL, B9.TL
NETS = {}

# articulation = |cut vertices| of exp9's t3_articulation_points: same all-sources search, count instead of list
NETS["t3_articulation"] = lambda K: (B9.r9("articulation_points.hvm.txt")
    .replace("// t3_articulation_points (GRAPH-SWING-2, runs/exp9)", "// t3_articulation (GRAPH-SWING-3, runs/exp19; count of exp9's t3_articulation_points)")
    .replace("@ap_zero = (* (0 *))", "@ap_zero = (* 0)")
    .replace("  & @wbits ~ (C (Wb (0 ((0 *) out))))", "  & @wpc ~ (C (Wb out))")
    + stream("w", K, "ap_step", "ap_fin") + X.msbfs() + X.bitrows() + X.mex() + Y.wpc() + PEEL_BITS() + SSSP() + TRIE)


# SCC: two msbfs loops (forward / reversed) + AND + lowest bit
SCC = lambda K, zero, output: (r19("scc.hvm.txt").replace("ZERO", zero).replace("OUTPUT", output)
    + stream("w", K, "sc_step", "sc_fin") + X.msbfs() + X.mex() + Y.wlow() + Y.scc_out() + PEEL_BITS() + ZL() + TRIE)
NETS["t3_scc_label"] = lambda K: SCC(K, "(0 *)", "@sccl ~ (Sf (Sb (L8 (0 ((n W5) ((0 *) out))))))")
NETS["t3_scc_count"] = lambda K: SCC(K, "0", "@sccc ~ (Sf (Sb (L8 (0 ((n W5) out)))))")


# ---- BFS family, composed from genome/lib/graphprims.py (exp8 style): unit-weight frontier rounds
sys.path.insert(0, os.path.dirname(R))
from genome.lib import graphprims as G
INF = 16777215
UND_W = lambda w: f"""((L g) ((u v) (L3 g3)))
  & L ~ {{L1 {{L2 L3}}}}
  & u ~ {{u1 {w and "{u2 u3}" or "u2"}}}
  & v ~ {{v1 {w and "{v2 v3}" or "v2"}}}
  & @gl_adj ~ (g (u1 (L1 ((v1 {w and "u3" or "1"}) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 {w and "v3" or "1"}) g3))))"""   # undirected edge -> two pushes, weight 1 (or the sender id)


def text(b): return b.text()


SP_ACT = """(b (d (c (d2 (f m)))))
  & c ~ {c1 {c2 c3}}
  & d ~ {dA {dB dC}}
  & c1 ~ $([<] $(dA lt))
  & c2 ~ $([>] $(b gt))
  & lt ~ $([>] $(gt f0))
  & f0 ~ {f1 fx}
  & dC ~ $([=] $(16777214 isT))
  & isT ~ $([+] $(1 mul))
  & fx ~ $([*] $(mul f))
  & f1 ~ ?((@gl_sel1 @gl_sel2s) (dB (c3 nd)))
  & nd ~ {d2 m}"""


def sp_len(K):
    """BFS from s (unit-weight frontier rounds) that STOPS in the round t is reached: t's leaf starts at the marker
    16777214, and a leaf that accepts a candidate while holding the marker raises flag 2 instead of 1; the loop goes on
    only while the OR of the flags is exactly 1. In unit-weight synchronous rounds the first value t accepts is its
    distance. Answer D[t] (marker -> 16777215). s == t answers 0 without reading the edge list."""
    b = G.Book(); G.lg(b); G._sel(b); G.adjacency(b); G.get(b, "gt"); G.const_trie(b, "gl_inf", str(INF))
    G.update(b, "seed", "min"); G.update(b, "mark", "set")
    G.frontier(b, "sp", SP_ACT, "(m (w r))\n  & m ~ $([+] $(w r))", "min", str(INF))
    b.defs["sp_loop"] = b.defs["sp_loop"].replace("  & any ~ ?((@sp_done", "  & any ~ $([=] $(1 go))\n  & go ~ ?((@sp_done")
    G.stream(b, "w", K, UND_W(False), "((* g) g)")
    b.add("""
@prog = ((n (s (t es))) out)
  & s ~ {s1 s2}
  & t ~ {t1 t2}
  & s1 ~ $([=] $(t1 eq))
  & eq ~ ?((@p_go @p_same) (n (s2 (t2 (es out)))))
@p_same = (* (* (* (* (* 0)))))
@p_go = (n (s (t (es out))))
  & n1 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 {L4 {L5 {L6 {L7 L8}}}}}}}
  & t ~ {ta tb}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @gl_inf ~ (L3 Dz)
  & @mark ~ (Dz (ta (L4 (16777214 D0))))
  & @gl_inf ~ (L5 Ci)
  & @seed ~ (Ci (s (L6 (0 C0))))
  & @sp_loop ~ ((G (D0 (C0 (L7 16777215)))) D)
  & n ~ n1
  & @gt ~ (D (tb (L8 got)))
  & got ~ {g1 g2}
  & g1 ~ $([=] $(16777214 un))
  & g2 ~ $([|] $(un out))
""")
    return text(b)


def khop(K):
    """BFS from s with budget k (only distances <= k are accepted, so rounds <= k + 1); count leaves i < n with
    D[i] <= k. The reference counts d <= k with d = 16777215 for unreachable vertices, so k = 16777215 gives n (every
    vertex counts); that case and k = 0 (answer 1) exit before reading the edge list."""
    b = G.Book(); G.lg(b); G.sssp(b, "sp"); G.adjacency(b)
    G.stream(b, "w", K, UND_W(False), "((* g) g)")
    G.reduce(b, "kc", """(x (i ((n k) o)))
  & i ~ $([<] $(n a))
  & x ~ $([>] $(k g))
  & g ~ $([^] $(1 le))
  & a ~ $([&] $(le o))""", "+", idx=True, env=True)
    b.add("""
@prog = ((n (s (k es))) out)
  & k ~ {ka kb}
  & ka ~ $([=] $(0 kz))
  & kz ~ ?((@kh_nz @kh_zero) (n (s (kb (es out)))))
@kh_zero = (* (* (* (* (* 1)))))
@kh_nz = (n (s (k (es out))))
  & k ~ {ka kb}
  & ka ~ $([=] $(16777215 ki))
  & ki ~ ?((@kh_go @kh_all) (n (s (kb (es out)))))
@kh_all = (* (n (* (* (* n)))))
@kh_go = (n (s (k (es out))))
  & n ~ {n1 {n2 n3}}
  & n3 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 L4}}}
  & k ~ {k1 k2}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @sp_sssp ~ (n1 (s (L3 (k1 (G D)))))
  & @kc ~ (D (L4 (0 ((n2 k2) out))))
""")
    return text(b)


def tree_parents(K):
    """BFS from r with packed labels hops*4096 + parent: an edge (u v) stores the sender id as the arc weight, the
    message is (label & ~4095) + 4096 + sender, combined by min. Output leaf x -> x & 4095, or 16777215 at the root."""
    b = G.Book(); G.lg(b); G._sel(b); G.adjacency(b); G.const_trie(b, "gl_inf", str(INF)); G.update(b, "seed", "min")
    G.frontier(b, "tp", G.RELAX, "(m (w r))\n  & m ~ $([&] $(16773120 mh))\n  & mh ~ $([+] $(w a))\n  & a ~ $([+] $(4096 r))",
               "min", str(INF))
    G.stream(b, "w", K, UND_W(True), "((* g) g)")
    b.add("@tl_drop = (* (t t))\n@tl_keep = (* (y (t (1 (y t)))))")
    G.fold(b, "tl", """(x (i (n (acc o))))
  & i ~ $([<] $(n keep))
  & x ~ {x1 x2}
  & x1 ~ $([>] $(4095 nr))
  & x2 ~ $([&] $(4095 p))
  & nr ~ $([^] $(1 isr))
  & isr ~ $([*] $(16777215 m))
  & m ~ $([|] $(p y))
  & keep ~ ?((@tl_drop @tl_keep) (y (acc o)))""")
    b.add("""
@prog = ((n (r es)) out)
  & n ~ {n1 n2}
  & n1 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 {L4 {L5 {L6 L7}}}}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @gl_inf ~ (L3 D0)
  & @gl_inf ~ (L4 Ci)
  & @seed ~ (Ci (r (L5 (0 C0))))
  & @tp_loop ~ ((G (D0 (C0 (L6 16777215)))) D)
  & @tl ~ (D (L7 (0 (n2 ((0 *) out)))))
""")
    return text(b)


NETS["t3_sp_len"] = sp_len
NETS["t3_khop"] = khop
NETS["t3_tree_parents__bfs"] = tree_parents
# Euler tour + pointer jumping (no BFS rounds)
ZI = lambda: (lambda w: w[w.index("@zi = "):w.index("@zl = ")])(B9.r5("sssp.hvm.txt"))
NETS["t3_tree_parents"] = lambda K: (r19("tree_parents_et.hvm.txt") + stream("w", K, "tp_step", "tp_fin") + Y.euler()
    + X.mc() + TL() + (lambda w: w[w.index("@pn_act"):w.index("@cfa =")])(X.peel()) + nav("pn", "pn_act") + ZI() + ZL() + TRIE)

if __name__ == "__main__":
    which = sys.argv[1]; K = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    for prog in (sorted(NETS) if which == "all" else [which]):
        open(os.path.join(D, prog + ".hvm"), "w").write(NETS[prog](K))
