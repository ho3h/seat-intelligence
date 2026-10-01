"""Pipeline side of the chatbot comparison: 20 policies x 20 samples (T=0.7) through model -> program -> net on the real 34 guests.
   python3 -m genome.hero1.compare"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, sys, collections
sys.path.insert(0, _REPO)
from genome.hero1.lang import parse, to_text, violations, load_real, ParseError
from genome.hero1.pipeline import run_net_assign, judge
from genome.hero1.baseline import selected


def main(path=_REPO + "/runs/hero1/samples/base20_t07.json"):
    S = json.load(open(path))["samples"]; guests, _ = load_real(); pols = {p["id"]: p for p in selected()}
    per = {}; tot = collections.Counter()
    for pid, texts in S.items():
        gold = parse(pols[pid]["gold"]); progs = collections.Counter(); assigns = set(); v_emit = v_stated = 0; rerun_same = 0; ok = 0; n = 0
        for t in texts:
            n += 1
            try: pol = parse(t)
            except ParseError: tot["unparsed"] += 1; continue
            a, _ = run_net_assign(guests, pol); a2, _ = run_net_assign(guests, pol)
            rerun_same += (a == a2 and a is not None)
            progs[to_text(pol)] += 1; assigns.add(json.dumps(a))
            ve = violations(guests, pol, a)["total"]; vs = violations(guests, gold, a)["total"]
            v_emit += ve > 0; v_stated += vs > 0
            ok += judge(t, pols[pid]["gold"])["passed"]
        per[pid] = dict(n=n, distinct_programs=len(progs), distinct_assignments=len(assigns), samples_violating_emitted_rules=v_emit,
                        samples_violating_stated_rules=v_stated, rerun_identical=f"{rerun_same}/{n}", passed_4lists=ok)
        for k in ("n", "samples_violating_emitted_rules", "samples_violating_stated_rules", "passed_4lists"):
            tot[k] += per[pid][k]
        tot["rerun_identical"] += rerun_same
    out = dict(totals=dict(tot), mean_distinct_programs=round(sum(x["distinct_programs"] for x in per.values()) / len(per), 2),
               mean_distinct_assignments=round(sum(x["distinct_assignments"] for x in per.values()) / len(per), 2), per_policy=per)
    json.dump(out, open(_REPO + "/runs/hero1/pipeline_vs_chatbot.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "per_policy"}, indent=1))
    for k, v in per.items(): print(k, v)


if __name__ == "__main__": main()
