"""Collect results for group 3: copy g3/out/<prog>.bend -> runs/exp17/<prog>.bend and write results_group3.json."""
import json, glob, os, shutil
R = "/Users/tedsandtads/Genome"
G = f"{R}/runs/exp17/g3"
progs = open(f"{R}/data/fair_bend_group3.txt").read().split()
notes = json.load(open(f"{G}/notes.json")) if os.path.exists(f"{G}/notes.json") else {}
out = {}
for p in progs:
    prev = None
    for d in sorted(glob.glob(f"{R}/runs/g1*/b1/seed0/{p}/state.json")):
        s = json.load(open(d))
        b = s.get("best") or {}
        if s.get("accepted") and b.get("depth_median_big") is not None:
            prev = b["depth_median_big"] if prev is None else min(prev, b["depth_median_big"])
    rec = {"status_seed0": None, "status_seed1": None, "depth": None, "itrs": None, "depth_seed1": None,
           "notes": notes.get(p, ""), "previous_bend_depth_or_null": prev}
    for s in (0, 1):
        f = f"{G}/res/{p}.seed{s}.json"
        if os.path.exists(f):
            r = json.load(open(f)); rec[f"status_seed{s}"] = r["status"]
            if s == 0: rec["depth"] = r["metrics"]["depth_median_big"]; rec["itrs"] = r["metrics"]["itrs_median_big"]
            else: rec["depth_seed1"] = r["metrics"]["depth_median_big"]
    if rec["status_seed0"] == "pass" and rec["status_seed1"] == "pass" and os.path.exists(f"{G}/out/{p}.bend"):
        shutil.copy(f"{G}/out/{p}.bend", f"{R}/runs/exp17/{p}.bend")
    wf = json.load(open(f"{G}/walkfloor.json")).get(p, {}) if os.path.exists(f"{G}/walkfloor.json") else {}
    rec["list_walk_floor_depth"] = wf.get("walk_median")
    rc = json.load(open(f"{R}/runs/g1_recount.json")).get(p, {})
    rec["frozen_native_depth"] = rc.get("depth")
    rec["source"] = f"runs/exp17/{p}.bend (built from runs/exp17/g3/src/{p}.bend + g3/lib)"
    out[p] = rec
json.dump(out, open(f"{R}/runs/exp17/results_group3.json", "w"), indent=1)
import math
rat = [o["previous_bend_depth_or_null"] / o["depth"] for o in out.values() if o["depth"] and o["previous_bend_depth_or_null"]]
for p, o in out.items(): print(f"{p:32s} {o['status_seed0']} {o['status_seed1']} depth={o['depth']} itrs={o['itrs']} prev={o['previous_bend_depth_or_null']}")
print("n improved", sum(1 for x in rat if x > 1), "of", len(rat), "geomean ratio", round(math.exp(sum(map(math.log, rat)) / len(rat)), 2) if rat else None)
