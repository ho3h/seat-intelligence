"""Depth slope per candidate: first k candidates of the n=144 seed-0 big case, with and without mnl."""
import sys, os
sys.path.insert(0, os.getcwd())
from genome.corpus import load_all
from genome.verify import build_cases, assemble
from genome.executor import run_net
p = load_all()["t5_conflict_greedy"]; net = open(sys.argv[1]).read()
x = [c for c in build_cases(p, 0) if c[0] == "big" and c[1] == 144][0][2]
n, mnl, cs = x
for k in (0, 50, 100, 200):
    for mm in (mnl, []):
        r = run_net(assemble(p, net, (n, mm, cs[:k])), "depth", 600)
        print(k, len(mm), r.depth, r.itrs, flush=True)
