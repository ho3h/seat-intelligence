"""Build + verify one exp19 net with at most 2 worker threads: python runs/exp19/v.py <prog> [seeds=0] [K=16]"""
import sys, os, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from build import NETS
from genome.corpus import load_all
from genome.verify import verify
prog = sys.argv[1]
seeds = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "0").split(",")]
K = int(sys.argv[3]) if len(sys.argv) > 3 else 16
out = os.path.join(D, prog + ".hvm")
open(out, "w").write(NETS[prog](K))
p = load_all()[prog]
for s in seeds:
    t = time.time()
    r = verify(p, open(out).read(), s, timeout=60, workers=2)
    print(prog, "seed", s, r["status"], r.get("metrics"), r.get("counterexample") or "", r.get("reason") or "", f"{time.time()-t:.0f}s", flush=True)
