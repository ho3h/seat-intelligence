"""Judge sampled programs against the frozen test set and aggregate.  python3 -m genome.hero1.evaluate <samples.json> [out.json]"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, sys, random, collections
sys.path.insert(0, _REPO)
from genome.hero1.pipeline import judge

import os
TEST = os.environ.get("TEST_FILE", _REPO + "/data/hero/policies_test.json")


def boot(xs, B=4000, seed=0):
    r = random.Random(seed); n = len(xs); ms = sorted(sum(r.choice(xs) for _ in range(n)) / n for _ in range(B))
    return ms[int(0.025 * B)], ms[int(0.975 * B)]


def main(path, out=None):
    pols = {p["id"]: p for p in json.load(open(TEST))["policies"] if p.get("scope", "in") == "in"}
    S = json.load(open(path)); samples = {k: v for k, v in S["samples"].items() if k in pols}
    per, rows = {}, []
    for pid, texts in samples.items():
        p = pols[pid]; js = []
        for t in texts:
            j = judge(t, p["gold"]); j["text"] = t; js.append(j)
        per[pid] = dict(voice=p["voice"], held=p.get("heldout_combo"), n=len(js), passed=sum(j["passed"] for j in js),
                        text_match=sum(j["text_match"] for j in js), parsed=sum(j["parsed"] for j in js),
                        samples=js)
    ids = sorted(per)
    pass1 = [per[i]["passed"] / per[i]["n"] for i in ids]
    def agg(sel):
        sel = list(sel); v = [per[i]["passed"] / per[i]["n"] for i in sel]
        tot_p = sum(per[i]["passed"] for i in sel); tot_n = sum(per[i]["n"] for i in sel)
        return dict(policies=len(sel), samples=tot_n, passed=tot_p, pass1=round(sum(v) / len(v), 4) if v else None,
                    ci=[round(x, 4) for x in boot(v)] if v else None,
                    text_match=round(sum(per[i]["text_match"] for i in sel) / tot_n, 4) if tot_n else None,
                    parsed=round(sum(per[i]["parsed"] for i in sel) / tot_n, 4) if tot_n else None)
    res = dict(source=path, overall=agg(ids), heldout_combo=agg(i for i in ids if per[i]["held"]),
               seen_combo=agg(i for i in ids if not per[i]["held"]),
               by_voice={v: agg(i for i in ids if per[i]["voice"] == v) for v in sorted({per[i]["voice"] for i in ids})},
               by_heldout={h: agg(i for i in ids if per[i]["held"] == h) for h in sorted({per[i]["held"] for i in ids if per[i]["held"]})},
               policy_pass=collections.OrderedDict((i, f"{per[i]['passed']}/{per[i]['n']}") for i in ids))
    json.dump(dict(result=res, per=per), open(out or path.replace(".json", ".scored.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return res


if __name__ == "__main__": main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
