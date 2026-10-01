"""Per big case (seed 0): m, Bend walk floor (a bare length walk over the edge list), this Bend, native (runs/exp5)."""
import sys, json
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.corpus import load_all
from genome.verify import build_cases, assemble
from genome import bend_io as B
from genome.executor import run_net
from genome.types import Tup
P = "t3_wsp_all_from t3_budget_reach t3_sources_sinks t3_triangle_count t3_line_graph_edges t3_dag_longest t3_cc_count t3_in_out_degrees".split()
A = load_all(); out = {}
for pid in P:
    p = A[pid]; k = len(p.inp.elems)
    pat = "(" + ", ".join([f"a{i}" for i in range(k - 1)] + ["es"]) + ")"
    walk = f"def prog(x):\n  {pat} = x\n  return len(es, 0)\n\ndef len(es, a):\n  match es:\n    case List/Nil:\n      return a\n    case List/Cons:\n      return len(es.tail, a + 1)\n"
    wbook, e1 = B.compile_bend(B.bend_source(p, walk)); assert not e1, e1
    mbook, e2 = B.compile_bend(B.bend_source(p, open(f"{pid}.bend").read())); assert not e2, e2
    nbook = open(f"/Users/tedsandtads/Genome/runs/exp5/{pid}.hvm").read()
    rows = []
    for kind, n, x in build_cases(p, 0):
        if kind != "big": continue
        w = run_net(B.assemble_bend(p, wbook, x, digest=False), "depth", 120)
        mb = run_net(B.assemble_bend(p, mbook, x, digest=False), "depth", 120)
        nv = run_net(assemble(p, nbook, x), "depth", 120)
        rows.append(dict(n=n, m=len(x[-1]), walk=w.depth, bend=mb.depth, bend_itrs=mb.itrs, native=nv.depth, native_itrs=nv.itrs))
    out[pid] = rows
    print(pid, [(r["m"], r["walk"], r["bend"], r["native"]) for r in rows], flush=True)
json.dump(out, open("compare.json", "w"), indent=1)
