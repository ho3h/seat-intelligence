"""Verify nets with genome.verify.verify (unmodified) using few worker processes (machine is shared).
usage: python3 runs/exp8/vfy.py <prog> <net.hvm> [seeds=0,1,2] [workers=4]"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genome.corpus import load_all
from genome.verify import verify
prog, net = sys.argv[1], sys.argv[2]
seeds = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "0,1,2").split(",")]
W = int(sys.argv[4]) if len(sys.argv) > 4 else 3
p = load_all()[prog]; book = open(net).read(); res = {}
for s in seeds:
    t = time.time(); r = verify(p, book, s, 60.0, W)
    res[s] = r
    print(json.dumps({"prog": prog, "seed": s, "status": r["status"], "metrics": r.get("metrics"), "secs": round(time.time()-t, 1),
                      "cx": r.get("counterexample"), "reason": (r.get("reason") or "")[:800]}), flush=True)
    if r["status"] != "pass": break
