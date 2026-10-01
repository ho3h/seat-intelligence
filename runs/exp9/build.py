"""Builds the GRAPH-SWING-2 nets (runs/exp9) from hand-written HVM2 text (*.hvm.txt here), the exp5 templates
(runs/exp5: stream, nav, trie/sssp primitives) and the new templates in lib_ext.py.
usage: python runs/exp9/build.py <prog> [K]"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__)); E5 = os.path.join(os.path.dirname(D), "exp5")
sys.path.insert(0, E5); sys.path.insert(0, D)
from lib import stream, nav
import lib_ext as X
r5 = lambda f: open(os.path.join(E5, f)).read()
r9 = lambda f: open(os.path.join(D, f)).read()
TRIE = r5("trie.hvm.txt")
SSSP = lambda: r5("sssp.hvm.txt") + nav("mu", "mu_act") + nav("gp", "gp_act")
NETS = {}

NETS["t3_wsp_dist"] = lambda K: r9("wsp_dist.hvm.txt") + X.und_adj("wd") + stream("w", K, "wd_step", "wd_fin") + X.get() + SSSP() + TRIE

NETS["t3_euler_start"] = lambda K: (r9("euler_start.hvm.txt") + stream("w", K, "eu_step", "eu_fin") + r9("idt.hvm.txt") + X.minmax()
    + nav("ic", "ic_act") + SSSP() + TRIE)

TL = lambda: (lambda w: w[w.index("// tl(t, L"):])(r5("wsp.hvm.txt"))
NETS["t3_greedy_coloring"] = lambda K: (r9("greedy_coloring.hvm.txt") + stream("w", K, "gc_step", "gc_fin") + X.mex()
    + X.mc() + nav("oa", "oa_act") + TL() + TRIE)

NETS["t3_count_shortest_paths"] = lambda K: (r9("count_shortest_paths.hvm.txt") + stream("w", K, "cs_step", "cs_fin")
    + X.get() + X.mc() + SSSP() + TRIE)

NETS["t3_lex_shortest_path"] = lambda K: (r9("lex_shortest_path.hvm.txt") + stream("w", K, "lx_step", "lx_fin")
    + X.get() + X.mc() + X.minmax() + SSSP() + TRIE)

ZL = lambda: (lambda w: w[w.index("@zl = "):w.index("// initial state")])(r5("sssp.hvm.txt"))
NETS["t3_kcore_size"] = lambda K: r9("kcore_size.hvm.txt") + stream("w", K, "kc_step", "kc_fin") + X.peel() + ZL() + TRIE

PEEL_BITS = lambda: (lambda w: w[w.index("@ad_act"):w.index("@cfa =")])(X.peel()) + nav("pn", "pn_act") + nav("ad", "ad_act")
MSB = lambda K, girth=False, pop=False: (r9("msb_prog.hvm.txt") + X.und_nb("w") + stream("w", K, "w_step", "w_fin")
    + X.msbfs(girth, pop) + PEEL_BITS() + ZL() + TRIE)
NETS["t3_eccentricities"] = lambda K: r9("eccentricities.hvm.txt") + MSB(K) + TL()
NETS["t3_wiener_index"] = lambda K: r9("wiener_index.hvm.txt") + MSB(K, pop=True)
NETS["t3_girth"] = lambda K: r9("girth.hvm.txt") + MSB(K, girth=True)

NETS["t3_articulation_points"] = lambda K: (r9("articulation_points.hvm.txt") + stream("w", K, "ap_step", "ap_fin")
    + X.msbfs() + X.bitrows() + PEEL_BITS() + SSSP() + TRIE)

NETS["t3_walk_count"] = lambda K: (r9("walk_count.hvm.txt") + stream("w", K, "wc_step", "wc_fin") + X.rounds()
    + X.get() + PEEL_BITS() + ZL() + TRIE)

NETS["t3_cheapest_k_walk"] = lambda K: (r9("cheapest_k_walk.hvm.txt") + stream("w", K, "ck_step", "ck_fin") + X.rounds()
    + X.get() + SSSP() + TRIE)

NETS["t3_mst_second"] = lambda K: (r9("mst_second.hvm.txt") + r9("ki.hvm.txt") + stream("w", K, "ms_step", "ms_fin") + X.prim(True)
    + SSSP() + TRIE)

NETS["t3_msf_weight"] = lambda K: (r9("msf_weight.hvm.txt") + r9("ki.hvm.txt") + X.und_adj("mf") + stream("w", K, "mf_step", "mf_fin")
    + X.prim(False) + SSSP() + TRIE)

SSSP_MAX = lambda: SSSP().replace("  & n1 ~ $([+] $(w1 cand))", "  & @max ~ (n1 (w1 cand))")
NETS["t3_minimax_path"] = lambda K: (r9("minimax_path.hvm.txt") + X.und_adj("mm") + stream("w", K, "mm_step", "mm_fin") + X.get()
    + SSSP_MAX() + X.minmax() + TRIE)

NETS["t3_max_degree_vertex"] = lambda K: (r9("max_degree_vertex.hvm.txt") + stream("w", K, "md_step", "md_fin")
    + (lambda w: w[w.index("@ad_act"):w.index("@pn_act")])(X.peel()) + nav("ad", "ad_act") + TRIE)

NETS["t3_clique_number"] = lambda K: (r9("clique_number.hvm.txt") + stream("w", K, "cq_step", "cq_fin") + X.bitrows()
    + X.mc() + X.get() + X.minmax() + PEEL_BITS() + ZL() + TRIE)

SSSP_BFS_PARENT = lambda: SSSP().replace("  & n1 ~ $([+] $(w1 cand))", "  & n1 ~ $([&] $(16773120 nh))\n  & nh ~ $([+] $(w1 cand))")
NETS["t3_max_flow"] = lambda K: (r9("max_flow.hvm.txt") + stream("w", K, "mf_step", "mf_fin") + X.get() + X.minmax()
    + "@stn_act = (* (x x))\n" + nav("stn", "stn_act") + nav("csub", "csub_act") + nav("cadd", "cadd_act") + SSSP_BFS_PARENT() + TRIE)

def MF_BODY(K):
    t = NETS["t3_max_flow"](K)
    i = t.index("@prog = "); j = t.index("@mf_triv = ")
    return t[:i] + t[j:]
NETS["t3_bipartite_matching"] = lambda K: (r9("bipartite_matching.hvm.txt") + stream("wg", K, "bg_step", "bg_fin")
    + stream("wx", K, "ix_step", "ix_fin") + nav("xa", "xa_act") + MF_BODY(K))

NETS["t3_apsp_matrix"] = lambda K: (r9("apsp_matrix.hvm.txt") + stream("w", K, "ap_step", "ap_fin") + X.vfront() + X.minmax()
    + X.zrows()
    + TL() + SSSP() + TRIE)

NETS["t3_forest_mis"] = lambda K: (r9("forest_mis.hvm.txt") + stream("w", K, "fm_step", "fm_fin") + X.mc() + X.minmax()
    + SSSP() + TRIE)

if __name__ == "__main__":
    prog = sys.argv[1]; K = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    open(os.path.join(D, prog + ".hvm"), "w").write(NETS[prog](K))
