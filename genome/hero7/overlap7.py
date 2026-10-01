"""Overlap of the R7 training texts with every test set: exact normalized matches, shared word 6-grams (both must be 0 after the
gen_train7 filter), and the share of test n-grams (n = 1..5) that occur anywhere in training (as reported in HERO-1/HERO-6).
Also the same numbers for the 30B paraphrases alone.  python -m genome.hero7.overlap7 -> runs/hero7/overlap7.json"""
import json, sys
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
sys.path.insert(0, _REPO)
from genome.hero7.gen_train7 import TESTS, norm, grams, read_rows


def main():
    tr = [norm(t) for t, _ in read_rows(_REPO + "/runs/hero7/data/train.jsonl")]
    tr += [norm(t) for t, _ in read_rows(_REPO + "/runs/hero7/data/valid.jsonl")]
    para = []
    try:
        from genome.hero7.gen_train7 import para_rows
        para = [norm(t) for t, _ in para_rows(10 ** 6)[0]]
    except Exception: pass
    out = {}
    for name, src in (("train_all", tr), ("para_only", para)):
        G = {n: set().union(*[grams(t, n) for t in src]) if src else set() for n in range(1, 7)}
        S = set(src); res = {}
        for p in TESTS:
            d = json.load(open(p)); ps = d["policies"] if isinstance(d, dict) else d
            T = [norm(x["text"]) for x in ps]
            r = dict(exact=sum(t in S for t in T), with_shared_6gram=sum(bool(grams(t, 6) & G[6]) for t in T))
            for n in range(1, 6):
                tg = [g for t in T for g in grams(t, n)]
                r[f"share_{n}gram"] = round(sum(g in G[n] for g in tg) / max(1, len(tg)), 3)
            res[p.split("/")[-1]] = r
        out[name] = res
    json.dump(out, open(_REPO + "/runs/hero7/overlap7.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__": main()
