"""Run verify_b1 on a Bend file; print status + metrics; save json to runs/exp17/g3/res/<tag>.seed<s>.json.
usage: vb.py prog path [seeds=0,1]"""
import sys, json, os, time
sys.path.insert(0, "<home>/Genome")
from genome.corpus import load_all
from genome.verify import verify_b1
prog, path = sys.argv[1], sys.argv[2]
seeds = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "0,1").split(",")]
p = load_all()[prog]
tag = os.path.basename(path)[:-5]
for seed in seeds:
    t = time.time()
    r = verify_b1(p, open(path).read(), seed=seed, workers=2, timeout=60)
    r["secs"] = round(time.time() - t, 1)
    print(tag, "seed", seed, r["status"], r.get("metrics"), r["secs"], "s")
    if r["status"] != "pass":
        print(json.dumps(r.get("counterexample") or r.get("reason"), default=str)[:1500])
    json.dump(r, open(f"<home>/Genome/runs/exp17/g3/res/{tag}.seed{seed}.json", "w"), default=str, indent=1)
    if r["status"] != "pass": break
