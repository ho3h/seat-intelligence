"""Compare constrained (C), same-loop unconstrained control (U) and the original baseline (A) on the iid test.

  python3 -m genome.exp2.analyze   -> runs/exp2/summary.json
"""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
from genome.exp.metrics import summarize, paired, boot_ci

FILES = {"A_baseline_batchgen": "runs/exp/A_native_v1_iid.scored.json", "U_sameloop_unconstrained": "runs/exp2/U_native_v1_iid.scored.json",
         "C_constrained": "runs/exp2/C_native_v1_iid.scored.json"}


def rates(path):
    S = json.load(open(path))["scored"]; per = collections.defaultdict(list)
    for v in S.values():
        for k in ("pass", "fail", "static", "noblock"):
            per[k].append(sum(s["status"] == k for s in v) / len(v))
    out = {f"{k}_rate": round(sum(x) / len(x), 4) for k, x in per.items()}
    out.update({f"{k}_rate_boot95": boot_ci(x) for k, x in per.items() if k in ("static", "fail")})
    why = collections.Counter()
    for v in S.values():
        for s in v:
            if s["status"] == "fail": why[(s.get("why") or "")[:45]] += 1
    out["fail_why_top"] = why.most_common(6)
    return out


def main():
    res = {}
    for k, f in FILES.items():
        p = os.path.join(ROOT, f)
        if not os.path.exists(p): continue
        s = summarize(p); s.update(rates(p)); res[k] = s
        raw = p.replace(".scored.json", ".json"); d = json.load(open(raw))
        if "stats" in d:
            st = [x for v in d["stats"].values() for x in v]; n = len(st)
            res[k]["decode"] = {"tok_per_s": round(d["meta"]["tok_per_s"], 1), "gen_seconds": round(d["meta"]["gen_seconds"]),
                                "mean_tokens": round(sum(x["tokens"] for x in st) / n, 1), "hit_max_rate": round(sum(x["hit_max"] for x in st) / n, 4),
                                "ended_clean_rate": round(sum(x["final_clean"] and x["final_mode"] == 3 for x in st) / n, 4),
                                "samples_with_any_masking": round(sum(x["steps_masked"] > 0 for x in st) / n, 4),
                                "mean_masked_steps": round(sum(x["steps_masked"] for x in st) / n, 2),
                                "slow_path_steps": sum(x["slow"] for x in st), "dead_ends": sum(x["dead"] for x in st)}
        else:
            res[k]["decode"] = {"seconds_total": round(d["meta"]["seconds"])}
    pa = lambda a, b: paired(os.path.join(ROOT, FILES[a]), os.path.join(ROOT, FILES[b])) if all(os.path.exists(os.path.join(ROOT, FILES[x])) for x in (a, b)) else None
    res["delta_C_minus_A"] = pa("A_baseline_batchgen", "C_constrained")
    res["delta_C_minus_U"] = pa("U_sameloop_unconstrained", "C_constrained")
    res["delta_U_minus_A"] = pa("A_baseline_batchgen", "U_sameloop_unconstrained")
    json.dump(res, open(os.path.join(ROOT, "runs/exp2/summary.json"), "w"), indent=1)
    keys = ["tasks", "samples", "pass@1", "pass@1_task_boot95", "pass@8", "static_rate", "static_rate_boot95", "fail_rate", "fail_rate_boot95",
            "noblock_rate", "static_classes", "pass_given_static_clean", "static_filter_best_of_8", "decode", "fail_why_top"]
    for k, v in res.items():
        print(k, json.dumps({x: v[x] for x in keys if x in v} if isinstance(v, dict) and "tasks" in v and "samples" in v else v))


if __name__ == "__main__": main()
