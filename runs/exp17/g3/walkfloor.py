"""Depth of a bare Bend walk over every list in the input (parallel), per big case at seed 0: the list-walk floor."""
import sys, json
sys.path.insert(0, "<home>/Genome")
from genome.corpus import load_all
from genome import bend_io as B
from genome.verify import build_cases
from genome.executor import run_net
from genome.types import List, Tup
A = load_all()
out = {}
for prog in open("<home>/Genome/data/fair_bend_group3.txt").read().split():
    p = A[prog]; t = p.inp
    if isinstance(t, Tup):
        names = [f"x{i}" for i in range(len(t.elems))]
        body = f"  ({', '.join(names)}) = x\n  return " + " + ".join([f"len({nm}, 0)" for nm, e in zip(names, t.elems) if isinstance(e, List)] or ["0"])
    else:
        body = "  return len(x, 0)"
    src = "def prog(x):\n" + body + "\n\ndef len(es, a):\n  match es:\n    case List/Nil:\n      return a\n    case List/Cons:\n      return len(es.tail, a + 1)\n"
    book, err = B.compile_bend(B.bend_source(p, src))
    if err: print(prog, err); continue
    ds = []
    for kind, n, x in build_cases(p, 0):
        if kind != "big": continue
        r = run_net(B.assemble_bend(p, book, x, digest=False), "depth", 120)
        ds.append(r.depth)
    med = sorted(ds)[len(ds) // 2]
    out[prog] = {"walk_depths": ds, "walk_median": med}
    print(prog, med, ds)
json.dump(out, open("<home>/Genome/runs/exp17/g3/walkfloor.json", "w"), indent=1)
