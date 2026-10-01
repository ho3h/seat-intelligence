"""Per-case metrics for one exp19 net on the big cases of a seed: python runs/exp19/probe.py <prog> [seed] [netfile]"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
from genome.corpus import load_all
from genome.verify import build_cases, assemble
from genome.executor import run_net
prog = sys.argv[1]; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
net = open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), prog + ".hvm")).read()
p = load_all()[prog]
for kind, n, x in build_cases(p, seed):
    if kind != "big": continue
    r = run_net(assemble(p, net, x), "depth", 120)
    print(n, "m=%d" % len(x[-1]), x[1:-1], "exp", p.ref(x) if not isinstance(p.ref(x), list) else "list", "itrs", r.itrs, "depth", r.depth, flush=True)
