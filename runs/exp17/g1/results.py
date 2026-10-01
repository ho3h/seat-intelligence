"""Collect group-1 results into runs/exp17/results_group1.json from g1/<prog>.seed{0,1}.json."""
import json, os
D = "/Users/tedsandtads/Genome/runs/exp17"
G = "/Users/tedsandtads/Genome"
progs = open(f"{G}/data/fair_bend_group1.txt").read().split()
nat = json.load(open(f"{G}/runs/g1_recount.json"))
notes = json.load(open(f"{D}/g1/notes.json"))
out = {}
for p in progs:
    r = {}
    for s in (0, 1):
        f = f"{D}/g1/{p}.seed{s}.json"
        r[s] = json.load(open(f)) if os.path.exists(f) else None
    st = f"{G}/runs/g1/b1/seed0/{p}/state.json"
    prev = json.load(open(st)).get("best") if os.path.exists(st) else None
    m0 = r[0]["metrics"] if r[0] else {}
    out[p] = {"status_seed0": r[0]["status"] if r[0] else None, "status_seed1": r[1]["status"] if r[1] else None,
              "depth": m0.get("depth_median_big"), "itrs": m0.get("itrs_median_big"), "depth_max": m0.get("depth_max"),
              "depth_seed1": r[1]["metrics"]["depth_median_big"] if r[1] else None,
              "notes": notes.get(p, ""),
              "previous_bend_depth_or_null": prev.get("depth_median_big") if prev else None,
              "previous_bend_itrs": prev.get("itrs_median_big") if prev else None,
              "native_depth": nat.get(p, {}).get("depth"), "native_itrs": nat.get(p, {}).get("itrs"),
              "source": f"runs/exp17/{p}.bend (built from runs/exp17/g1/src/{p}.bend + g1/src/lib.bend by g1/build.py)"}
json.dump(out, open(f"{D}/results_group1.json", "w"), indent=1)
import math
rat = [o["previous_bend_depth_or_null"] / o["depth"] for o in out.values() if o["depth"] and o["previous_bend_depth_or_null"]]
ratn = [o["depth"] / o["native_depth"] for o in out.values() if o["depth"] and o["native_depth"]]
print("programs", len(out), "passing both", sum(o["status_seed0"] == "pass" and o["status_seed1"] == "pass" for o in out.values()))
print("geomean prev/new depth", math.exp(sum(map(math.log, rat)) / len(rat)), "min", min(rat), "max", max(rat))
print("geomean new/native depth", math.exp(sum(map(math.log, ratn)) / len(ratn)))
for p, o in out.items():
    print(f"{p:26s} {o['status_seed0']}/{o['status_seed1']} depth {o['depth']} itrs {o['itrs']} | prev {o['previous_bend_depth_or_null']} / {o['previous_bend_itrs']} | native {o['native_depth']} / {o['native_itrs']}")
