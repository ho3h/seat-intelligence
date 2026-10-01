"""Verify a net with 2 worker processes (machine is loaded). usage: python3 runs/exp18/v.py <prog> <net> [seeds...]"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genome.verify import verify
from genome.corpus import load_all
prog, net = sys.argv[1], sys.argv[2]
seeds = [int(s) for s in sys.argv[3:]] or [0]
p = load_all()[prog]
for s in seeds:
    t = time.time()
    r = verify(p, open(net).read(), s, 60.0, workers=2)
    print(prog, "seed", s, r["status"], r.get("metrics"), r.get("counterexample") or "", r.get("reason") or "", f"{time.time()-t:.0f}s", flush=True)
