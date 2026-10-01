"""Scaling table for docs/RECON-REALDATA.md from the runs/exp16 logs. usage: python3 -m genome.exp16.report"""
import json, math, os, glob
from .run import RUNS


def load(pattern):
    out = {}
    for f in glob.glob(os.path.join(RUNS, pattern)):
        for l in open(f):
            try: d = json.loads(l)
            except Exception: continue
            out[(d.get("net"), d.get("mode"), d["N"])] = d
    return out


R = load("*.log")
B = {d["N"]: d for d in map(json.loads, open(os.path.join(RUNS, "baselines.jsonl")))}
BL = {}
if os.path.exists(os.path.join(RUNS, "baseline_list.jsonl")):
    BL = {d["N"]: d for d in map(json.loads, open(os.path.join(RUNS, "baseline_list.jsonl")))}
NS = [2000, 8000, 32000, 100000]


def g(net, mode, N, k):
    d = R.get((net, mode, N)); return None if d is None else d.get(k)


def fmt(x, nd=2):
    if x is None: return "-"
    if isinstance(x, bool): return "yes" if x else "NO"
    if isinstance(x, float): return f"{x:,.{nd}f}"
    return f"{x:,}"


def expo(a, b, na=2000, nb=100000):
    return None if not a or not b else math.log(b / a) / math.log(nb / na)


for net in ("fan", "bal", "full", "list"):
    print(f"\n### net = {net}\n")
    print("| N | accepted edges | must-not-link | LP rounds R | depth | interactions (oracle) | correct (Rust / C) | Rust interp s | "
          "arm64 C s (8 thr) | max RSS Rust / C MB |")
    print("| --- " * 10 + "|")
    for N in NS:
        d = R.get((net, "rust", N)) or R.get((net, "native", N)) or {}
        print(f"| {N:,} | {fmt(d.get('accepted'))} | {fmt(d.get('mnl'))} | {fmt(d.get('lp_rounds'))} | {fmt(g(net, 'depth', N, 'depth'))} | "
              f"{fmt(g(net, 'depth', N, 'itrs'))} | {fmt(g(net, 'rust', N, 'correct'))} / {fmt(g(net, 'native', N, 'correct'))} | "
              f"{fmt(g(net, 'rust', N, 'rt_secs'))} | {fmt(g(net, 'native', N, 'rt_secs'))} | "
              f"{fmt(g(net, 'rust', N, 'max_rss_mb'), 0)} / {fmt(g(net, 'native', N, 'max_rss_mb'), 0)} |")
    ex = {k: expo(g(net, m, 2000, f), g(net, m, 100000, f)) for k, (m, f) in
          dict(depth=("depth", "depth"), itrs=("depth", "itrs"), rust=("rust", "rt_secs"), native=("native", "rt_secs")).items()}
    print("\nexponents 2k->100k: " + ", ".join(f"{k} {v:.2f}" for k, v in ex.items() if v is not None))

print("\n### union-find baselines (union + canon only, seconds)\n")
print("| N | Python | Rust (x86_64, Rosetta) | C (arm64) | HVM2 fan, Rust interp | HVM2 fan, arm64 C | C runtime / C union-find |")
print("| --- " * 7 + "|")
for N in NS:
    b = B.get(N, {}); nat = g("fan", "native", N, "rt_secs")
    print(f"| {N:,} | {b.get('py_uf_secs', 0):.4f} | {b.get('rust_uf_x86_secs', 0):.6f} | {b.get('c_uf_arm64_secs', 0):.6f} | "
          f"{fmt(g('fan', 'rust', N, 'rt_secs'))} | {fmt(nat)} | {nat / b['c_uf_arm64_secs']:,.0f}x |" if b and nat else f"| {N:,} | - |")

print("\n### same-data baseline: RECON-SWING net, linked-list input\n")
for N, d in sorted(BL.items()):
    print(N, {k: d.get(k) for k in ("depth", "itrs_bare", "rust_secs", "correct", "max_rss_mb", "err", "depth_err")})
