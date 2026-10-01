"""Wall-clock context for swing 20: hand-written union-find in Python, Rust (x86_64 under Rosetta, like `hvm run`) and C
(native arm64, like the C runtime) on the same slices. Union + canon only (parsing excluded), checked against the net's
Python reference. usage: python3 -m genome.exp16.baselines N..."""
import json, os, subprocess, sys, time
from .data import slice_
from .run import reference, RUNS
def h(canon):
    x = 0
    for i, c in enumerate(canon): x = (x * 1000003 + (c ^ i)) & (2**64 - 1)
    return x
for N in map(int, sys.argv[1:]):
    s = slice_(N); canon, _ = reference(s)
    ts = []
    for _ in range(5):
        t = time.perf_counter(); reference(s); ts.append(time.perf_counter() - t)
    inp = f"{s['n']} {s['tau']} {len(s['edges'])}\n" + "\n".join(f"{u} {v} {sc}" for u, v, sc in s["edges"]) + "\n"
    rec = dict(N=N, py_uf_secs=min(ts))
    for name, cmd in (("rust_uf_x86", [os.path.join(RUNS, "uf_rs")]), ("c_uf_arm64", ["arch", "-arm64", os.path.join(RUNS, "uf_c")])):
        out = subprocess.run(cmd, input=inp, capture_output=True, text=True).stdout
        d = dict(l.split() for l in out.strip().splitlines())
        rec[name + "_secs"] = float(d["secs"]); rec[name + "_correct"] = int(d["canon"]) == h(canon)
    print(json.dumps(rec), flush=True)
    with open(os.path.join(RUNS, "baselines.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
