"""HERO-7 scoring of a samples file (genome/hero7/sample7.py) on one test set.
  set 1 / set 2: unchanged HERO-1 judge (genome.hero1.pipeline.judge; avoid/pair lines are parse errors)
  set 6: genome/hero6/judge6.py (lenient 3-list criterion + STRICT)
  set 7: genome/hero7/judge7.py (lenient + STRICT; STRICT is the headline)
pass@1 of a policy = passed / n; headline = mean over policies.
VOTE (self-consistency): the n samples of a request are run through the seating reference (lang6.assign_ref) on the request's
guest list (genome.hero7.sample7.request_guests); samples are grouped by the SEATING they produce (unparsable samples do not vote
unless all are unparsable); the largest group wins (tie: the group whose first sample came first); its most common canonical
program (tie: first) is the vote's answer, which is then judged like one sample.
  python -m genome.hero7.score7 <set: 1|2|6|7> <samples.json> [out.json]"""
import collections, json, sys
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
sys.path.insert(0, _REPO)
from genome.hero6 import lang6 as L
SETS = {"1": _REPO + "/data/hero/policies_test.json", "2": _REPO + "/data/hero/policies_test2.json",
        "6": _REPO + "/data/hero/policies_test6.json", "7": _REPO + "/data/hero/policies_test7.json"}


def judges(setid):
    if setid in ("1", "2"):
        from genome.hero1.pipeline import judge
        def j(t, g):
            r = judge(t, g); return r["passed"], r["passed"]
        return j
    if setid == "6": from genome.hero6.judge6 import judge, judge_strict
    else: from genome.hero7.judge7 import judge, judge_strict
    def j(t, g):
        r = judge(t, g)
        return r["passed"], (judge_strict(t, g) if r["passed"] else False)
    return j


def vote(texts, guests):
    groups = collections.OrderedDict(); bad = []
    for t in texts:
        try:
            pol = L.parse(t); key = tuple(L.assign_ref(guests, pol)); c = L.to_text(pol)
        except Exception:
            bad.append(t); continue
        groups.setdefault(key, []).append(c)
    if not groups: return bad[0] if bad else "", 0
    best = max(groups.values(), key=len)            # max keeps the first maximal group (insertion order)
    cnt = collections.Counter(best); top = max(cnt.values())
    return next(c for c in best if cnt[c] == top), len(best)


def score(setid, path, out=None):
    from genome.hero7.sample7 import request_guests
    d = json.load(open(SETS[setid])); pols = {p["id"]: p for p in (d["policies"] if isinstance(d, dict) else d) if p.get("scope", "in") == "in"}   # set 2: 72 in-scope (as HERO-1)
    S = json.load(open(path))["samples"]; J = judges(setid); G = request_guests(SETS[setid])
    per = {}
    for pid, texts in S.items():
        g = pols[pid]["gold"]; js = [J(t, g) for t in texts]
        v = vote(texts, G) if len(texts) > 1 else (texts[0], 1)
        vj = J(v[0], g)
        per[pid] = dict(n=len(texts), passed=sum(a for a, _ in js), strict=sum(b for _, b in js), vote_text=v[0], vote_size=v[1],
                        vote_pass=bool(vj[0]), vote_strict=bool(vj[1]), samples=texts, gold=g, text=pols[pid]["text"])
    ids = sorted(per); P = len(ids); N = sum(per[i]["n"] for i in ids)
    res = dict(set=setid, source=path, policies=P, samples=N,
               passed=sum(per[i]["passed"] for i in ids), strict=sum(per[i]["strict"] for i in ids),
               pass1=round(sum(per[i]["passed"] / per[i]["n"] for i in ids) / P, 4),
               pass1_strict=round(sum(per[i]["strict"] / per[i]["n"] for i in ids) / P, 4),
               vote_pass=sum(per[i]["vote_pass"] for i in ids), vote_strict=sum(per[i]["vote_strict"] for i in ids))
    if setid == "7":
        for name, sel in (("named", [i for i in ids if pols[i]["names_guests"]]), ("category_only", [i for i in ids if not pols[i]["names_guests"]]),
                          ("invented", [i for i in ids if pols[i]["invented"]])):
            res[name] = dict(policies=len(sel), strict=sum(per[i]["strict"] for i in sel), samples=sum(per[i]["n"] for i in sel),
                             pass1_strict=round(sum(per[i]["strict"] / per[i]["n"] for i in sel) / len(sel), 4),
                             vote_strict=sum(per[i]["vote_strict"] for i in sel))
    json.dump(dict(result=res, per=per), open(out or path.replace(".json", ".scored.json"), "w"), indent=1)
    return res


if __name__ == "__main__":
    print(json.dumps(score(*sys.argv[1:]), indent=1))
