"""Builds the GRAPH-SWING nets in runs/exp5 from hand-written HVM2 text plus the stream() block-walker macro.
usage: python runs/exp5/build.py <prog> [K] [outfile]"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from lib import stream, nav
TRIE = open(os.path.join(D, "trie.hvm.txt")).read()
NETS = {}

NETS["t3_sources_sinks"] = lambda K: """// t3_sources_sinks (GRAPH-SWING, runs/exp5). Two bitmaps as complete binary tries keyed by vertex id; each edge is
// one pre-expanded "set leaf" insert into each trie; the edge list is consumed by a k-cell blocked stream walker.
// sources = n - |{v}|, sinks = n - |{u}|.
@prog = ((n es) out)
  & n ~ ?((@ss_zero @ss_pos) (es out))
@ss_zero = (* (0 0))
@ss_pos = (nm1 (es out))
  & nm1 ~ {a b}
  & a ~ $([+1] n1)
  & @lg ~ (b d)
  & d ~ {d1 {d2 d3}}
  & @zt ~ (d1 to0)
  & @zt ~ (d2 ti0)
  & @w_blk ~ (es ((d3 (to0 ti0)) (cout cin)))
  & n1 ~ {n2 n3}
  & n2 ~ $([-] $(cin src))
  & n3 ~ $([-] $(cout snk))
  & out ~ (src snk)
@ss_step = ((d (to ti)) ((u v) (d3 (to2 ti2))))
  & d ~ {d1 {d2 d3}}
  & @ins ~ (to (u (d1 to2)))
  & @ins ~ (ti (v (d2 ti2)))
@ss_fin = ((d (to ti)) (co ci))
  & d ~ {d1 d2}
  & @cnt ~ (to (d1 co))
  & @cnt ~ (ti (d2 ci))
""" + stream("w", K, "ss_step", "ss_fin") + TRIE

NETS["t3_line_graph_edges"] = lambda K: """// t3_line_graph_edges (GRAPH-SWING, runs/exp5). Degree histogram as a complete binary trie keyed by vertex id:
// each edge is two pre-expanded "increment leaf" updates; the answer is a tree reduction of d*(d-1)/2 over the leaves.
@prog = ((n es) out)
  & n ~ ?((@lg_zero @lg_pos) (es out))
@lg_zero = (* 0)
@lg_pos = (nm1 (es out))
  & @lg ~ (nm1 d)
  & d ~ {d1 d2}
  & @zt ~ (d1 t0)
  & @w_blk ~ (es ((d2 t0) out))
@le_step = ((d t) ((u v) (d3 t2)))
  & d ~ {d1 {d2 d3}}
  & @inc ~ (t (u (d1 t1)))
  & @inc ~ (t1 (v (d2 t2)))
@le_fin = ((d t) o)
  & @pairs ~ (t (d o))
// inc(t, k, L): add 1 to leaf k
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
// pairs(t, L): sum over leaves of x*(x-1)/2
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
""" + stream("w", K, "le_step", "le_fin") + TRIE

NETS["t3_triangle_count"] = lambda K: (open(os.path.join(D, "tc.hvm.txt")).read() + stream("w", K, "tc_step", "tc_fin")
    + nav("sb", "sb_act") + nav("sr", "sr_act") + nav("pu", "pu_act") + nav("ad", "ad_act") + TRIE)

SSSP_FILE = os.environ.get("SSSP", "sssp.hvm.txt")  # variants: sssp_lookahead.hvm.txt, sssp_ungated.hvm.txt
SSSP = lambda: open(os.path.join(D, SSSP_FILE)).read() + nav("mu", "mu_act") + nav("gp", "gp_act")
NETS["t3_wsp_all_from"] = lambda K: (open(os.path.join(D, "wsp.hvm.txt")).read() + stream("w", K, "wsp_step", "wsp_fin")
    + SSSP() + TRIE)

NETS["t3_budget_reach"] = lambda K: (open(os.path.join(D, "budget.hvm.txt")).read() + stream("w", K, "br_step", "br_fin")
    + SSSP() + TRIE)

NETS["t3_dag_longest"] = lambda K: (open(os.path.join(D, "dag.hvm.txt")).read() + stream("w", K, "dl_step", "dl_fin")
    + nav("pu", "pu_act") + nav("mx", "mx_act") + TRIE)

def _inc_tl():
    le = NETS["t3_line_graph_edges"](4)
    inc = le[le.index("// inc(t, k, L)"):le.index("// pairs(t, L)")]
    w = open(os.path.join(D, "wsp.hvm.txt")).read()
    return inc + w[w.index("// tl(t, L"):]
NETS["t3_in_out_degrees"] = lambda K: (open(os.path.join(D, "iod.hvm.txt")).read() + stream("w", K, "io_step", "io_fin")
    + _inc_tl() + TRIE)

NETS["t3_cc_count"] = lambda K: (open(os.path.join(D, "cc.hvm.txt")).read() + stream("w", K, "cc_step", "cc_fin")
    + SSSP() + TRIE)

if __name__ == "__main__":
    prog = sys.argv[1]; K = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(D, prog + ".hvm")
    open(out, "w").write(NETS[prog](K))
