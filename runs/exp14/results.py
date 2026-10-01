"""exp14 results: per condition, pass rate on seed 0 (within 6 attempts), pass rate on seeds 0-2 (the passing net
re-verified on seeds 1 and 2), attempts, failure classes, metrics of passing nets.
usage: python3 runs/exp14/results.py [cond ...]  -> runs/exp14/results.json + table on stdout.
Failure classes come from runs/exp14/classify.json (hand classification of every failed attempt, keyed
"<cond>/<prog>/<attempt>"), falling back to an automatic guess."""
import sys, os, json, glob, fcntl
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(D)))
from genome.corpus import load_all
from genome.verify import verify

PROGS = ['t3_reach_count', 't3_sp_len', 't3_cc_label', 't3_sp_count', 't5_decide_count', 't5_decide_filter',
         't5_decide_singleton', 't5_conflict_count', 't5_conflict_flags', 't5_rewrite_sameas_roots']
CONDS = sys.argv[1:] or ["unchecked", "checked"]
CL = json.load(open(os.path.join(D, "classify.json"))) if os.path.exists(os.path.join(D, "classify.json")) else {}
CACHE = os.path.join(D, "seeds12.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}


def auto(fb):
    if fb.startswith("REJECTED"): return "glue"
    if "did not run" in fb: return "glue?"
    return "algo?"


out = {}
ps = load_all()
for c in CONDS:
    rows = []
    for p in PROGS:
        log = os.path.join(D, c, p, "attempts.jsonl")
        recs = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
        ge = os.path.join(D, c, p, "glue_errors.log")
        n_glue = open(ge).read().count("--- ") if os.path.exists(ge) else 0
        passed = [r for r in recs if r["status"] == "pass"]
        row = {"prog": p, "attempts": len(recs), "seed0": bool(passed), "glue_errors_caught": n_glue,
               "fails": [{"attempt": r["attempt"], "class": CL.get(f"{c}/{p}/{r['attempt']}", auto(r["feedback"])),
                          "feedback": r["feedback"][:300]} for r in recs if r["status"] != "pass"]}
        if passed:
            k = passed[0]["attempt"]; net = os.path.join(D, c, p, f"attempt{k}.hvm")
            row["metrics0"] = passed[0]["metrics"]
            key = f"{c}/{p}/{k}"
            if key not in cache:
                book = open(net).read(); res = {}
                with open(os.path.join(D, ".verify.lock"), "w") as lk:
                    fcntl.flock(lk, fcntl.LOCK_EX)
                    for s in (1, 2):
                        r = verify(ps[p], book, s, 60.0, 3)
                        res[s] = {"status": r["status"], "cx": r.get("counterexample")}
                cache[key] = res; json.dump(cache, open(CACHE, "w"), indent=1, default=str)
            row["seeds012"] = all(v["status"] == "pass" for v in cache[key].values())
            row["seed12_cx"] = {s: v["cx"] for s, v in cache[key].items() if v["status"] != "pass"}
        else:
            row["seeds012"] = False
        rows.append(row)
    out[c] = rows

json.dump(out, open(os.path.join(D, "results.json"), "w"), indent=1, default=str)
for c, rows in out.items():
    done = [r for r in rows if r["attempts"]]
    print(f"\n== {c}: {len(done)} programs attempted")
    for r in rows:
        m = r.get("metrics0") or {}
        print(f"  {r['prog']:26s} att {r['attempts']}  seed0 {'PASS' if r['seed0'] else 'fail'}  0-2 {'PASS' if r['seeds012'] else '-'}"
              f"  glueErrs {r['glue_errors_caught']:2d}  depth {m.get('depth_median_big')} itrs {m.get('itrs_median_big')}"
              f"  fails {[f['class'] for f in r['fails']]}")
    n = len(done) or 1
    s0 = sum(r["seed0"] for r in done); s2 = sum(r["seeds012"] for r in done)
    fl = [f["class"] for r in done for f in r["fails"]]
    pa = [r["attempts"] for r in done if r["seed0"]]
    print(f"  seed0 {s0}/{len(done)}  seeds0-2 {s2}/{len(done)}  mean attempts (passing) "
          f"{sum(pa) / len(pa) if pa else float('nan'):.2f}  mean attempts (all) {sum(r['attempts'] for r in done) / n:.2f}"
          f"  failure classes {dict((k, fl.count(k)) for k in sorted(set(fl)))}")
