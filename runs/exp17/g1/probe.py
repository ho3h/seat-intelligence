"""Depth/itrs of a Bend source on the big cases of a program (no correctness check). usage: probe.py prog file [seed]"""
import sys, json, statistics
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.corpus import load_all
from genome.verify import build_cases
from genome import bend_io as B
from genome.executor import run_net
p = load_all()[sys.argv[1]]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
book, err = B.compile_bend(B.bend_source(p, open(sys.argv[2]).read()))
if err: print(err); sys.exit(1)
out = []
for kind, n, x in build_cases(p, seed):
    if kind != "big": continue
    r = run_net(B.assemble_bend(p, book, x, digest=False), "depth", 120)
    out.append((r.depth, r.itrs)); print(n, r.depth, r.itrs, r.ok, flush=True)
print("median depth", sorted(d for d, _ in out)[len(out)//2])
