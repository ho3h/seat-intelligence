"""Same-session rerun of the native exp16 nets (fan, full) through exp16's own harness, so wall-clock and RSS of the
native arm and the Bend arm are measured under the same machine load. Nothing in genome/exp16 or runs/exp16 is touched;
results go to runs/exp21/native_rerun.jsonl. usage: NET=fan|full python3 -m genome.exp21.native_rerun <mode> N..."""
import json, os, sys
from ..exp16.run import run
from ..exp16.net import build
from ..exp16.net_full import build as build_full

RUNS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "runs/exp21")

if __name__ == "__main__":
    mode, var = sys.argv[1], os.environ.get("NET", "fan")
    net = build_full(2) if var == "full" else build(2, var)
    for N in map(int, sys.argv[2:]):
        rec = dict(arm="native", net=var, tpc_l2=int(os.environ.get("TPC_L2", "3")) if mode == "native" else None,
                   **run(mode, N, net, full=(var == "full")))
        print(json.dumps(rec), flush=True)
        with open(os.path.join(RUNS, "native_rerun.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
