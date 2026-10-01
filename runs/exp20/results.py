"""exp20 results: per condition (A = checked glue + primitives, B = A + recipes), pass on seed 0 within 6 attempts,
pass on seeds 0-2 (the passing net re-verified on seeds 1 and 2), attempts, failure classes (runs/exp20/classify.json,
hand classification keyed "<cond>/<prog>/<attempt>"), recipes used, paired sign test.
usage: python3 runs/exp20/results.py  -> runs/exp20/results.json + tables on stdout"""
import sys, os, json, re, fcntl
from math import comb
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(D)))
from genome.corpus import load_all
from genome.verify import verify

PROGS = ["t5_decide_normalise", "t5_decide_drop_known", "t5_decide_order", "t5_decide_top_k", "t5_decide_stage_cap",
         "t5_decide_stage_idem", "t5_conflict_pairs", "t5_prop_conflicts", "t5_prop_majority", "t5_rewrite_edges",
         "t5_rewrite_weighted", "t5_rewrite_collapsed", "t5_rewrite_degrees", "t5_rewrite_sameas_cycle",
         "t5_metric_pairwise", "t5_metric_rand"]
CONDS = ["A", "B"]
CL = json.load(open(os.path.join(D, "classify.json"))) if os.path.exists(os.path.join(D, "classify.json")) else {}
CACHE = os.path.join(D, "seeds12.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
RECIPES = ["list_length_and_copy", "list_to_trie", "filter_in_order", "count_where", "take_first", "argmax_first_trie",
           "argmax_first", "sort_by", "lookup_many", "reduce_by_key", "select_sorted", "count_where_trie",
           "frontier_relax", "layered_bfs_count", "pointer_jump"]


def auto(fb):
    if fb.startswith("REJECTED"): return "glue?"
    if "did not run" in fb: return "glue?"
    return "semantic?"


def recipes_used(path):
    if not os.path.exists(path): return []
    s = open(path).read()
    return sorted({r for r in RECIPES if re.search(r"R\.%s\(|recipes\.%s\(|\b%s\(P" % (r, r, r), s)})


ps = load_all()
out = {}
for c in CONDS:
    rows = []
    for p in PROGS:
        wd = os.path.join(D, c, p)
        log = os.path.join(wd, "attempts.jsonl")
        recs = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
        ge = os.path.join(wd, "glue_errors.log")
        n_glue = open(ge).read().count("--- ") if os.path.exists(ge) else 0
        passed = [r for r in recs if r["status"] == "pass"]
        final_build = os.path.join(wd, f"attempt{passed[0]['attempt']}_build.py") if passed else os.path.join(wd, "build.py")
        row = {"prog": p, "attempts": len(recs), "seed0": bool(passed), "glue_errors_caught": n_glue,
               "recipes": recipes_used(final_build),
               "fails": [{"attempt": r["attempt"], "class": CL.get(f"{c}/{p}/{r['attempt']}", auto(r["feedback"])),
                          "feedback": r["feedback"][:300]} for r in recs if r["status"] != "pass"]}
        if passed:
            k = passed[0]["attempt"]; net = os.path.join(wd, f"attempt{k}.hvm")
            row["metrics0"] = passed[0]["metrics"]
            key = f"{c}/{p}/{k}"
            if key not in cache:
                book = open(net).read(); res = {}
                with open(os.path.join(D, ".verify.lock"), "w") as lk:
                    fcntl.flock(lk, fcntl.LOCK_EX)
                    for s in (1, 2):
                        r = verify(ps[p], book, s, 60.0, 2)
                        res[s] = {"status": r["status"], "cx": r.get("counterexample")}
                cache[key] = res; json.dump(cache, open(CACHE, "w"), indent=1, default=str)
            row["seeds012"] = all(v["status"] == "pass" for v in cache[key].values())
            row["seed12_cx"] = {s: v["cx"] for s, v in cache[key].items() if v["status"] != "pass"}
        else:
            row["seeds012"] = False
        rows.append(row)
    out[c] = rows

for c, rows in out.items():
    print(f"\n== {c}")
    for r in rows:
        m = r.get("metrics0") or {}
        print(f"  {r['prog']:26s} att {r['attempts']}  seed0 {'PASS' if r['seed0'] else 'fail'}  0-2 {'PASS' if r['seeds012'] else '-'}"
              f"  glueErrs {r['glue_errors_caught']:2d}  depth {m.get('depth_median_big')} itrs {m.get('itrs_median_big')}"
              f"  recipes {r['recipes']}  fails {[f['class'] for f in r['fails']]}")
    s0 = sum(r["seed0"] for r in rows); s2 = sum(r["seeds012"] for r in rows)
    fl = [f["class"] for r in rows for f in r["fails"]]
    pa = [r["attempts"] for r in rows if r["seed0"]]
    print(f"  seed0 {s0}/{len(rows)}  seeds0-2 {s2}/{len(rows)}  mean attempts (passing) "
          f"{sum(pa) / len(pa) if pa else float('nan'):.2f}  mean attempts (all) {sum(r['attempts'] for r in rows) / len(rows):.2f}"
          f"  failure classes {dict((k, fl.count(k)) for k in sorted(set(fl)))}  glue errors caught {sum(r['glue_errors_caught'] for r in rows)}")
a = {r["prog"]: r["seeds012"] for r in out["A"]}; b = {r["prog"]: r["seeds012"] for r in out["B"]}
bo = sum(1 for p in PROGS if b[p] and not a[p]); ao = sum(1 for p in PROGS if a[p] and not b[p])
both = sum(1 for p in PROGS if a[p] and b[p]); none = sum(1 for p in PROGS if not a[p] and not b[p])
nd = bo + ao
pval = sum(comb(nd, k) for k in range(bo, nd + 1)) / 2 ** nd if nd else 1.0
summary = {"B_only": bo, "A_only": ao, "both": both, "neither": none, "sign_test_one_sided_p": pval,
           "passA": sum(a.values()), "passB": sum(b.values())}
print("\npaired:", summary)
out["paired"] = summary
json.dump(out, open(os.path.join(D, "results.json"), "w"), indent=1, default=str)
