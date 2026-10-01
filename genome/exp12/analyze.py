"""Summarise runs/exp12/results.jsonl -> runs/exp12/summary.json (+ printed tables for docs/LOOKAHEAD.md)."""
import glob, json, os, sys, statistics as S
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
os.chdir(ROOT)

ok = lambda s: s["accepted"] and s.get("audit") == ["pass", "pass"]
recs = [json.loads(l) for l in open("runs/exp12/results.jsonl")]
med = lambda v: S.median(v) if v else None


def best_k(r):
    """best passing K by seed-0 depth (ties -> fewer interactions)."""
    c = [(v["seeds"]["0"]["metrics"]["depth_median_big"], v["seeds"]["0"]["metrics"]["itrs_median_big"], int(k))
         for k, v in r["K"].items() if v["pass"] and v["seeds"]["0"]["metrics"]["depth_median_big"]]
    return min(c)[2] if c else None


def row(r):
    o = r["orig"]["metrics"] or {}
    out = {"set": r["set"], "pid": r["pid"], "applies": r.get("applies", False), "why": r.get("why"),
           "d0": o.get("depth_median_big"), "i0": o.get("itrs_median_big"), "is0": o.get("itrs_median_small"), "size0": r["size"],
           "orig_pass": r["orig"]["status"] == "pass"}
    if out["applies"]:
        out["pass_any"] = any(v["pass"] for v in r["K"].values())
        out["pass_all"] = all(v["pass"] for v in r["K"].values())
        out["perK"] = {}
        for k, v in r["K"].items():
            m = v["seeds"]["0"]["metrics"] or {}
            out["perK"][k] = {"pass": v["pass"], "d": m.get("depth_median_big"), "i": m.get("itrs_median_big"),
                              "is": m.get("itrs_median_small"), "size": v["size"],
                              "fail": None if v["pass"] else [s["cex"] or s["reason"] for s in v["seeds"].values() if s["status"] != "pass"][:1]}
        b = best_k(r)
        out["bestK"] = b
        if b is not None and out["d0"] and out["i0"]:
            v = out["perK"][str(b)]
            out["dgain"] = 1 - v["d"] / out["d0"]; out["igain"] = 1 - v["i"] / out["i0"]; out["sgrow"] = v["size"] / out["size0"]
            out["d_best"], out["i_best"] = v["d"], v["i"]
    return out


rows = [row(r) for r in recs]


def summary(rs, label):
    n = len(rs); ap = [r for r in rs if r["applies"]]
    pa = [r for r in ap if r.get("pass_any")]
    g = [r for r in pa if "dgain" in r]
    s = {"set": label, "nets": n, "applies": len(ap), "applies_frac": len(ap) / n if n else None,
         "pass_any": len(pa), "pass_all_K": sum(r.get("pass_all", False) for r in ap),
         "median_depth_gain_bestK": med([r["dgain"] for r in g]), "median_itrs_change_bestK": med([-r["igain"] for r in g]),
         "median_size_growth_bestK": med([r["sgrow"] for r in g]),
         "bestK_hist": {k: sum(r["bestK"] == k for r in g) for k in (2, 4, 8, 16)},
         "depth_gain_ge10": sum(r["dgain"] >= 0.10 for r in g)}
    for K in ("2", "4", "8", "16"):
        vv = [r for r in ap if K in r.get("perK", {})]
        pv = [r for r in vv if r["perK"][K]["pass"] and r["d0"] and r["perK"][K]["d"]]
        s[f"K{K}"] = {"pass": len(pv), "of": len(vv),
                      "median_depth_gain": med([1 - r["perK"][K]["d"] / r["d0"] for r in pv]),
                      "median_itrs_change": med([r["perK"][K]["i"] / r["i0"] - 1 for r in pv]),
                      "median_small_itrs_change": med([r["perK"][K]["is"] / r["is0"] - 1 for r in pv if r["is0"] and r["perK"][K]["is"]])}
    return s


out = {"primary": summary([r for r in rows if r["set"] in ("t1", "t2", "t3x16", "t3x1")], "T1+T2+T3(exp5, shipped + K=1 rebuild)"),
       "t1t2": summary([r for r in rows if r["set"] in ("t1", "t2")], "T1+T2"),
       "t3x16": summary([r for r in rows if r["set"] == "t3x16"], "T3 exp5 as shipped (K=16 stream)"),
       "t3x1": summary([r for r in rows if r["set"] == "t3x1"], "T3 exp5 rebuilt with K=1 stream"),
       "t4": summary([r for r in rows if r["set"] == "t4"], "T4"),
       "all": summary(rows, "all")}
why = {}
for r in rows:
    if not r["applies"]: why.setdefault((r["why"] or "")[:60], []).append(r["pid"])
out["not_applied_reasons"] = {k: v for k, v in sorted(why.items(), key=lambda x: -len(x[1]))}
out["failures"] = [(r["pid"], k, v["fail"]) for r in rows if r["applies"] for k, v in r["perK"].items() if not v["pass"]]

# ---------------------------------------------------------------- native vs Bend (plain Bend = frozen author's accepted B1)
def layers(pats):
    o = {}
    for pat in pats:
        for f in glob.glob(pat):
            s = json.load(open(f))
            if s["pid"] not in o or (not ok(o[s["pid"]]) and ok(s)): o[s["pid"]] = s
    return o


BB = layers(["runs/g1/b1/seed0/*/state.json", "runs/g1r1/b1/seed0/*/state.json", "runs/g1esc/b1/seed0/*/state.json"])
cmp_rows = []
for r in rows:
    if r["set"] not in ("t1", "t2", "t4") or not r["orig_pass"]: continue
    b = BB.get(r["pid"])
    if not b or not ok(b) or not b.get("best") or not b["best"].get("depth_median_big"): continue
    bd, bi = b["best"]["depth_median_big"], b["best"]["itrs_median_big"]
    nd, ni = r["d0"], r["i0"]
    td, ti = (r["d_best"], r["i_best"]) if "d_best" in r else (nd, ni)
    cmp_rows.append({"pid": r["pid"], "tier": r["set"], "bend_d": bd, "bend_i": bi, "nat_d": nd, "nat_i": ni, "la_d": td, "la_i": ti,
                     "transformed": "d_best" in r})


def cmpsum(rs, tag):
    if not rs: return None
    g0 = [max(1 - x["nat_i"] / x["bend_i"], 1 - x["nat_d"] / x["bend_d"]) for x in rs]
    g1 = [max(1 - x["la_i"] / x["bend_i"], 1 - x["la_d"] / x["bend_d"]) for x in rs]
    return {"tag": tag, "programs": len(rs), "transformed": sum(x["transformed"] for x in rs),
            "native_wins_orig": sum(g > 0 for g in g0), "native_wins_lookahead": sum(g > 0 for g in g1),
            "median_gain_orig": med(g0), "median_gain_lookahead": med(g1),
            "depth_wins_orig": sum(x["nat_d"] < x["bend_d"] for x in rs), "depth_wins_lookahead": sum(x["la_d"] < x["bend_d"] for x in rs),
            "median_depth_ratio_bend_over_native_orig": med([x["bend_d"] / x["nat_d"] for x in rs]),
            "median_depth_ratio_bend_over_native_lookahead": med([x["bend_d"] / x["la_d"] for x in rs])}


out["vs_bend"] = {t: cmpsum([x for x in cmp_rows if x["tier"] in t.split("+")], t) for t in ("t1", "t2", "t4", "t1+t2+t4")}
out["vs_bend_rows"] = cmp_rows

# ---------------------------------------------------------------- T3 vs strong Bend (docs/BEND-FAIR-BASELINE.md, runs/exp7)
strong = []
for r in rows:
    if r["set"] not in ("t3x1", "t3x16"): continue
    f = f"runs/exp7/{r['pid']}.seed0.json"
    if not os.path.exists(f): continue
    m = json.load(open(f))["metrics"]
    strong.append({"set": r["set"], "pid": r["pid"], "bend_d": m["depth_median_big"], "bend_i": m["itrs_median_big"], "nat_d": r["d0"], "nat_i": r["i0"],
                   "la_d": r.get("d_best", r["d0"]), "la_i": r.get("i_best", r["i0"]), "bestK": r.get("bestK")})
out["vs_strong_bend"] = strong
geo = lambda v: float(__import__("math").exp(S.mean([__import__("math").log(x) for x in v]))) if v else None
for st in ("t3x1", "t3x16"):
    ss = [x for x in strong if x["set"] == st]
    out[f"vs_strong_bend_{st}"] = {"geomean_bend_over_native_orig": geo([x["bend_d"] / x["nat_d"] for x in ss]),
                                   "geomean_bend_over_native_lookahead": geo([x["bend_d"] / x["la_d"] for x in ss])}
out["rows"] = rows
json.dump(out, open("runs/exp12/summary.json", "w"), indent=1, default=str)
for k in ("primary", "t1t2", "t3x16", "t3x1", "t4", "all"): print(json.dumps(out[k]))
print(json.dumps(out["vs_bend"], indent=0)); print(json.dumps({k: v for k, v in out.items() if k.startswith("vs_strong_bend_")}))
print(json.dumps(out["not_applied_reasons"], indent=0)[:3000]); print(out["failures"][:20])
