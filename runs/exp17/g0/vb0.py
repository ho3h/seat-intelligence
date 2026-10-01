"""group0 runner: verify_b1 on runs/exp17/<prog>.bend (or given path) for seeds; print status + metrics.
Saves runs/exp17/<prog>.seed<k>.json when the path is the canonical one and it passes."""
import sys, json, os, time
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.corpus import load_all
from genome.verify import verify_b1
D = "/Users/tedsandtads/Genome/runs/exp17"
prog = sys.argv[1]
path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else f"{D}/{prog}.bend"
path = os.path.abspath(path)
seeds = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "0").split(",")]
p = load_all()[prog]
for seed in seeds:
    t = time.time()
    r = verify_b1(p, open(path).read(), seed=seed, workers=2, timeout=60)
    m = r.get("metrics", {})
    print(prog, os.path.basename(path), "seed", seed, r["status"], "depth", m.get("depth_median_big"), "itrs", m.get("itrs_median_big"),
          "dmax", m.get("depth_max"), f"{time.time()-t:.0f}s", flush=True)
    if r["status"] != "pass":
        print(json.dumps({k: v for k, v in r.items() if k != "metrics"}, default=str)[:1500]); break
    if path == f"{D}/{prog}.bend":
        json.dump(r, open(f"{D}/{prog}.seed{seed}.json", "w"), default=str, indent=1)
