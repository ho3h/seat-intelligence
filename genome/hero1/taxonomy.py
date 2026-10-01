"""Failure taxonomy for sampled programs against gold: python3 -m genome.hero1.taxonomy <samples.scored.json>"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, sys, collections
sys.path.insert(0, _REPO)
from genome.hero1.lang import parse, ParseError, CATS

import os
TEST = os.environ.get("TEST_FILE", _REPO + "/data/hero/policies_test.json")


def diff(g, s):
    """list of (component, kind) differences between sample policy s and gold policy g"""
    d = []
    if s.cap != g.cap: d.append(("size", "wrong_number" if g.cap != 6 and s.cap != 6 else ("missing" if g.cap != 6 else "extra")))
    if s.tog_company != g.tog_company: d.append(("together_company", "missing" if g.tog_company else "extra"))
    a, b = set(g.tog_cats), set(s.tog_cats)
    for c in a - b: d.append(("together_cat", "missing"))
    for c in b - a: d.append(("together_cat", "extra_or_wrong_category"))
    gl, sl = list(g.limits), list(s.limits)
    for x in gl:
        if x in sl: continue
        same_cats = [y for y in sl if y[0] == x[0]]; same_k = [y for y in sl if y[1] == x[1]]
        d.append(("limit", "wrong_k" if same_cats else ("wrong_categories" if same_k else "missing")))
    for x in sl:
        if x not in gl and not any(y[0] == x[0] or y[1] == x[1] for y in gl): d.append(("limit", "extra"))
    ga, sa = set(g.aparts), set(s.aparts)
    for x in ga - sa: d.append(("apart", "missing_or_wrong_pair"))
    for x in sa - ga: d.append(("apart", "extra_or_wrong_pair"))
    if tuple(g.order) != tuple(s.order):
        if not g.order: d.append(("order", "extra"))
        elif not s.order: d.append(("order", "missing"))
        elif set(g.order) == set(s.order): d.append(("order", "wrong_sequence"))
        else: d.append(("order", "wrong_categories"))
    return d


def main(path):
    R = json.load(open(path)); per = R["per"]
    pols = {p["id"]: p for p in json.load(open(TEST))["policies"]}
    kinds = collections.Counter(); by_voice = collections.defaultdict(collections.Counter); nfail = 0; ex = collections.defaultdict(list)
    silent = 0
    for pid, e in per.items():
        g = parse(pols[pid]["gold"])
        for j in e["samples"]:
            if j["passed"]: continue
            nfail += 1
            if not j["parsed"]:
                k = ("parse_error", j["why"][:40]); kinds[k] += 1; by_voice[e["voice"]][k] += 1; continue
            d = diff(g, parse(j["text"]))
            if not d: silent += 1; d = [("no_structural_diff", "assignment_differs")]
            for k in d: kinds[k] += 1; by_voice[e["voice"]][k] += 1; ex[k].append((pid, j["text"].replace("\n", " ; ")))
    out = dict(failed_samples=nfail, components={f"{a}:{b}": n for (a, b), n in kinds.most_common()},
               by_voice={v: {f"{a}:{b}": n for (a, b), n in c.most_common()} for v, c in by_voice.items()},
               examples={f"{a}:{b}": v[:3] for (a, b), v in ex.items()})
    print(json.dumps(out, indent=1))
    json.dump(out, open(path.replace(".scored.json", ".taxonomy.json"), "w"), indent=1)


if __name__ == "__main__": main(sys.argv[1])
