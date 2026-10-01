"""Run verify_b1 on runs/exp17/<prog>.bend (or a given path); print status + metrics; save result json for the canonical file."""
import sys, json, os, time
sys.path.insert(0, "<home>/Genome")
from genome.corpus import load_all
from genome.verify import verify_b1
prog = sys.argv[1]
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
path = sys.argv[3] if len(sys.argv) > 3 else f"<home>/Genome/runs/exp17/{prog}.bend"
p = load_all()[prog]
t = time.time()
r = verify_b1(p, open(path).read(), seed=seed, workers=2, timeout=60)
out = {k: v for k, v in r.items() if k != "cases"}
out["secs"] = round(time.time() - t, 1)
print(os.path.basename(path), json.dumps(out, default=str)[:1500])
if r["status"] == "pass" and os.path.abspath(path) == f"<home>/Genome/runs/exp17/{prog}.bend":
    json.dump(r, open(f"<home>/Genome/runs/exp17/{prog}.seed{seed}.json", "w"), default=str, indent=1)
