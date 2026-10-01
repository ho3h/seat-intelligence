"""G1 recount with swarm authors: every native net from every source, re-verified on fresh seeds; per program keep the shallowest that passes."""
import glob, json, os, sys, statistics as S
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from genome.corpus import load_all
from genome.verify import verify
R = load_all()
ok = lambda s: s["accepted"] and s.get("audit") == ["pass", "pass"]
cands = {p: [] for p in R}
for pat in ("runs/g1/native/seed0", "runs/g1r1/native/seed0", "runs/probe2/dsv4/native/seed0", "runs/g1esc/native/seed0"):
    for f in glob.glob(pat + "/*/state.json"):
        s = json.load(open(f))
        b = os.path.join(os.path.dirname(f), "best.hvm")
        if ok(s) and os.path.exists(b) and s["pid"] in R: cands[s["pid"]].append(("g1:" + pat.split("/")[1], b, True))
for d in ("exp5", "exp8", "exp9", "exp10"):
    for f in glob.glob(f"runs/{d}/*.hvm"):
        b = os.path.basename(f)[:-4]
        if b in R: cands[b].append((d, f, False))
def check(job):
    pid, src, path, trusted = job
    net = open(path).read(); p = R[pid]
    seeds = (3, 4) if not trusted else (0,)
    rs = [verify(p, net, seed=s, timeout=40.0, workers=3) for s in seeds]
    if any(r["status"] != "pass" for r in rs): return pid, src, path, None
    m = rs[0]["metrics"]
    return pid, src, path, (m["itrs_median_big"], m["depth_median_big"])
jobs = [(p, s, path, t) for p, L in cands.items() for s, path, t in L]
print(len(jobs), "candidate nets over", sum(1 for L in cands.values() if L), "programs", flush=True)
res = {}
with ThreadPoolExecutor(3) as ex:
    for pid, src, path, m in ex.map(check, jobs):
        if m: res.setdefault(pid, []).append((m[1], m[0], src, path))
best = {p: min(v) for p, v in res.items()}
json.dump({p: {"depth": v[0], "itrs": v[1], "src": v[2], "path": v[3]} for p, v in best.items()}, open("runs/g1_recount.json", "w"))
print("native programs with an accepted, freshly re-verified net:", len(best), "/ 200")
from collections import Counter
print("by tier:", dict(sorted(Counter(p.split("_")[0] for p in best).items())))
print("best net source:", dict(Counter(v[2] for v in best.values())))
