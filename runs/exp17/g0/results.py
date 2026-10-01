"""Collect runs/exp17/results_group0.json from the per-seed verifier JSONs (written by g0/vb0.py)."""
import json, glob, os, math
D = "/Users/tedsandtads/Genome/runs/exp17"
progs = open("/Users/tedsandtads/Genome/data/fair_bend_group0.txt").read().split()
notes = json.load(open(f"{D}/g0/notes.json")) if os.path.exists(f"{D}/g0/notes.json") else {}
nat = json.load(open("/Users/tedsandtads/Genome/runs/g1_recount.json"))
out, ratios = {}, []
for p in progs:
    rec = {}
    for s in (0, 1):
        f = f"{D}/{p}.seed{s}.json"
        rec[f"status_seed{s}"] = json.load(open(f))["status"] if os.path.exists(f) else None
    m = json.load(open(f"{D}/{p}.seed0.json"))["metrics"] if os.path.exists(f"{D}/{p}.seed0.json") else {}
    rec["depth"] = m.get("depth_median_big"); rec["itrs"] = m.get("itrs_median_big")
    rec["depth_max"] = m.get("depth_max")
    s1 = f"{D}/{p}.seed1.json"
    rec["depth_seed1"] = json.load(open(s1))["metrics"]["depth_median_big"] if os.path.exists(s1) else None
    prev = None
    st = f"/Users/tedsandtads/Genome/runs/g1/b1/seed0/{p}/state.json"
    if os.path.exists(st):
        b = json.load(open(st)).get("best") or {}
        prev = b.get("depth_median_big"); rec["previous_bend_itrs"] = b.get("itrs_median_big")
    rec["previous_bend_depth_or_null"] = prev
    rec["native_depth"] = (nat.get(p) or {}).get("depth")
    rec["notes"] = notes.get(p, "")
    if prev and rec["depth"]: ratios.append(prev / rec["depth"])
    out[p] = rec
json.dump(out, open(f"{D}/results_group0.json", "w"), indent=1)
for p, r in out.items():
    print(f"{p:28s} {r['status_seed0']!s:5} {r['status_seed1']!s:5} depth {r['depth']!s:>7} itrs {r['itrs']!s:>9} prev {r['previous_bend_depth_or_null']!s:>8} native {r['native_depth']!s:>7}")
g = math.exp(sum(math.log(x) for x in ratios) / len(ratios)) if ratios else None
print("improved", sum(x > 1 for x in ratios), "of", len(ratios), "geomean prev/new depth", round(g, 2) if g else None)
