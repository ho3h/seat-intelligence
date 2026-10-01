"""Per-big-case depth/itrs for a Bend file: probe.py prog path [seed]"""
import sys, json
sys.path.insert(0, "<home>/Genome")
from genome.corpus import load_all
from genome.verify import build_cases
from genome import bend_io as B
from genome.executor import run_net
prog, path = sys.argv[1], sys.argv[2]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
p = load_all()[prog]
book, err = B.compile_bend(B.bend_source(p, open(path).read()))
if err: print(err); sys.exit(1)
for kind, n, x in build_cases(p, seed):
    if kind != "big": continue
    r = run_net(B.assemble_bend(p, book, x, digest=False), "depth", 120)
    ls = [len(e) for e in (x if isinstance(x, tuple) else (x,)) if isinstance(e, list)]
    ok = r.ok
    print(n, ls, "depth", r.depth, "itrs", r.itrs, "ok" if ok else "WRONG")
