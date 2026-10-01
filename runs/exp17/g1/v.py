"""Run verify_b1 on runs/exp17/<prog>.bend (or a given path); print status + metrics; save result json on pass.
usage: python runs/exp17/v.py <prog> [path] [seeds e.g. 0,1]"""
import sys, json, os, time
sys.path.insert(0, "<home>/Genome")
from genome.corpus import load_all
from genome.verify import verify_b1
prog = sys.argv[1]
D = "<home>/Genome/runs/exp17"
path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else f"{D}/{prog}.bend"
seeds = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "0").split(",")]
p = load_all()[prog]
for seed in seeds:
    t = time.time()
    r = verify_b1(p, open(path).read(), seed=seed, workers=2, timeout=60)
    m = r.get("metrics", {})
    print(f"{prog} seed{seed} {r['status']} depth={m.get('depth_median_big')} itrs={m.get('itrs_median_big')} "
          f"dmax={m.get('depth_max')} ({time.time()-t:.0f}s)", flush=True)
    if r["status"] != "pass":
        print(json.dumps({k: v for k, v in r.items() if k != "metrics"}, default=str)[:1500]); break
    json.dump(r, open(f"{D}/g1/{prog}.seed{seed}.json" if path == f"{D}/{prog}.bend" else f"{path[:-5]}.seed{seed}.json", "w"), default=str, indent=1)
