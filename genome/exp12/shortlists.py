"""Does lookahead width cost interactions on short lists (speculative cells erased past the end)?
Runs original and K in {2,4,8,16} transformed nets on lists of length n (single process), records itrs and depth.
-> runs/exp12/shortlists.json"""
import json, os, random, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
os.chdir(ROOT)
from genome.corpus import load_all
from genome.verify import assemble
from genome.types import decode
from genome.executor import run_net

R = load_all()
PROGS = {"t1_sum": "fold", "t1_map_inc": "map", "t1_filter_even": "filter", "t1_prefix_sums": "scan", "t1_max": "fold+switch"}
NS = list(range(0, 18)) + [31, 32, 33, 63, 64, 65, 128, 256, 512]
rng = random.Random(7)
out = {}
for pid, kind in PROGS.items():
    p = R[pid]
    nets = {"orig": open(f"runs/g1/native/seed0/{pid}/best.hvm").read()}
    for K in (2, 4, 8, 16):
        f = f"runs/exp12/nets/t1/{pid}.K{K}.hvm"
        if os.path.exists(f): nets[f"K{K}"] = open(f).read()
    out[pid] = {"kind": kind, "rows": []}
    for n in NS:
        x = [rng.randrange(0, 1000) for _ in range(n)]
        row = {"n": n}
        for tag, book in nets.items():
            txt = assemble(p, book, x)
            c = run_net(txt, "run", 60)
            okv = c.ok and decode(c.result, p.out) == p.ref(x)
            r = run_net(txt, "depth", 120)
            row[tag] = {"itrs": r.itrs, "depth": r.depth, "ok": okv}
        out[pid]["rows"].append(row)
        print(pid, n, {k: (v["itrs"], v["depth"], v["ok"]) for k, v in row.items() if k != "n"}, flush=True)
json.dump(out, open("runs/exp12/shortlists.json", "w"), indent=1)
