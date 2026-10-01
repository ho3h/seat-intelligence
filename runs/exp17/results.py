"""Collect runs/exp17/<prog>.seed{0,1}.json into runs/exp17/results_group2.json (depth/itrs = seed-0 medians)."""
import json, glob, os
D = "/Users/tedsandtads/Genome/runs/exp17"
NOTES = json.load(open(f"{D}/notes.json"))
progs = open("/Users/tedsandtads/Genome/data/fair_bend_group2.txt").read().split()
rec = json.load(open("/Users/tedsandtads/Genome/runs/g1_recount.json"))
out = {}
for p in progs:
    prev = []
    for f in glob.glob(f"/Users/tedsandtads/Genome/runs/g1*/b1/seed0/{p}/state.json"):
        b = json.load(open(f)).get("best")
        if b and b.get("depth_median_big"): prev.append((b["depth_median_big"], b["itrs_median_big"]))
    prev = min(prev) if prev else None
    r = {}
    for s in (0, 1):
        f = f"{D}/{p}.seed{s}.json"
        r[s] = json.load(open(f)) if os.path.exists(f) else None
    m0 = r[0]["metrics"] if r[0] else {}
    m1 = r[1]["metrics"] if r[1] else {}
    out[p] = {"status_seed0": r[0]["status"] if r[0] else "missing", "status_seed1": r[1]["status"] if r[1] else "missing",
              "depth": m0.get("depth_median_big"), "itrs": m0.get("itrs_median_big"), "depth_max": m0.get("depth_max"),
              "depth_seed1": m1.get("depth_median_big"), "itrs_seed1": m1.get("itrs_median_big"),
              "notes": NOTES.get(p, ""), "previous_bend_depth_or_null": prev[0] if prev else None,
              "previous_bend_itrs": prev[1] if prev else None,
              "native_depth_itrs_g1_recount": [rec[p].get("depth"), rec[p].get("itrs")] if p in rec else None}
json.dump(out, open(f"{D}/results_group2.json", "w"), indent=1)
import math
rat = [o["previous_bend_depth_or_null"] / o["depth"] for o in out.values() if o["depth"] and o["previous_bend_depth_or_null"]]
nat = [o["native_depth_itrs_g1_recount"][0] / o["depth"] for o in out.values() if o["depth"] and o["native_depth_itrs_g1_recount"]]
for p, o in out.items():
    print(f"{p:28s} {o['status_seed0']:5s} {o['status_seed1']:5s} depth {o['depth']!s:>7} itrs {o['itrs']!s:>9}  prev {o['previous_bend_depth_or_null']!s:>8}/{o['previous_bend_itrs']!s:>10}  native {o['native_depth_itrs_g1_recount']}")
g = lambda v: math.exp(sum(map(math.log, v)) / len(v))
print("geomean prev/new depth", round(g(rat), 2), "n", len(rat), "| geomean native/new depth", round(g(nat), 2))
