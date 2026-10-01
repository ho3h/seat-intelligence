"""Independence diagnostics: how much of the frozen test wording appears in the training texts.  python3 -m genome.hero1.overlap"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, re, sys
sys.path.insert(0, _REPO)


def toks(s): return re.findall(r"[a-z0-9']+", s.lower())


def ngrams(t, n): return {tuple(t[i:i + n]) for i in range(len(t) - n + 1)}


def main():
    test = json.load(open(_REPO + "/data/hero/policies_test.json"))["policies"]
    rows = [json.loads(l) for l in open(_REPO + "/runs/hero1/data/train.jsonl")]
    train = [r["messages"][0]["content"].split("## Policy\n\n")[1].split("\n\n## Reply")[0] for r in rows]
    tt = [toks(t) for t in train]
    tr = {n: set().union(*[ngrams(t, n) for t in tt]) for n in (1, 2, 3, 4, 5)}
    out = {"train_texts": len(train), "test_texts": len(test), "exact_text_in_train": sum(p["text"] in set(train) for p in test)}
    for n in (1, 2, 3, 4, 5):
        tot = hit = 0
        for p in test:
            g = ngrams(toks(p["text"]), n); tot += len(g); hit += len(g & tr[n])
        out[f"test_{n}gram_seen_in_train"] = round(hit / tot, 3)
    # nearest neighbour by 3-gram jaccard
    tg = [ngrams(t, 3) for t in tt]
    best = []
    for p in test:
        g = ngrams(toks(p["text"]), 3)
        b = max((len(g & h) / max(1, len(g | h)) for h in tg), default=0); best.append(b)
    best.sort(); out["nearest_train_3gram_jaccard_median"] = round(best[len(best) // 2], 3); out["nearest_train_3gram_jaccard_max"] = round(best[-1], 3)
    print(json.dumps(out, indent=1)); json.dump(out, open(_REPO + "/runs/hero1/overlap.json", "w"), indent=1)


main()
