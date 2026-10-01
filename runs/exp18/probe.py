"""Depth probe: big seed-0 cases of a program, plus ablations (no mnl, no cands). usage: probe.py <prog> <net>"""
import sys, os
sys.path.insert(0, os.getcwd())
from genome.corpus import load_all
from genome.verify import build_cases, assemble
from genome.executor import run_net
p = load_all()[sys.argv[1]]; net = open(sys.argv[2]).read()
for kind, n, x in build_cases(p, 0):
    if kind != "big": continue
    r = run_net(assemble(p, net, x), "depth", 600)
    line = f"n={n} m={len(x[-1]) if p.id=='t5_conflict_greedy' else '?'} depth={r.depth} itrs={r.itrs}"
    if p.id == "t5_conflict_greedy":
        r2 = run_net(assemble(p, net, (x[0], [], x[2])), "depth", 600)
        r3 = run_net(assemble(p, net, (x[0], x[1], [])), "depth", 600)
        line += f" | no-mnl depth={r2.depth} | no-cands depth={r3.depth}"
    print(line, flush=True)
