"""Run verify_b1 on runs/exp7/<prog>.bend; print status + metrics; save result json."""
import sys, json, os
sys.path.insert(0, "<home>/Genome")
from genome.corpus import load_all
from genome.verify import verify_b1
prog = sys.argv[1]; path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else f"<home>/Genome/runs/exp7/{prog}.bend"
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
p = load_all()[prog]
r = verify_b1(p, open(path).read(), seed=seed, workers=4, timeout=60)
print(json.dumps({k: v for k, v in r.items()}, default=str))
if r["status"] == "pass" and path.endswith(f"/{prog}.bend"):
    json.dump(r, open(f"<home>/Genome/runs/exp7/{prog}.seed{seed}.json", "w"), default=str, indent=1)
