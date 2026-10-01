"""Builds the fair in-distribution test set and the expert-iteration sampling pool (manifests of [family, index]).

  python3 -m genome.exp.sets

iid_test.json : 60 pipeline + 60 reduce tasks whose descriptions appear nowhere in train/indist (fresh compositions).
                Only these two train families still have unseen variants: the other six are exhausted by train.json.
ei_pool.json  : 150 pipeline + 150 reduce fresh tasks, disjoint from iid_test, plus up to 24 train.json tasks of each of the six
                small families (their verified solutions become extra, diverse positives; capped for sampling time).
                Holdout families are never touched.
"""
import json, os, sys
from ..taskgen import task, TRAIN_FAMILIES
from ..taskset import valid, OUT

SMALL = [f for f in TRAIN_FAMILIES if f not in ("pipeline", "reduce")]


def fresh(fam, seen, want, start):
    got, i = [], start
    while len(got) < want:
        p = task(fam, i)
        if p.desc not in seen:
            try: ok = valid(p)
            except Exception: ok = False
            if ok: seen.add(p.desc); got.append([fam, i])
        i += 1
    return got


def main():
    tr = json.load(open(os.path.join(OUT, "train.json"))); ind = json.load(open(os.path.join(OUT, "indist.json")))
    seen = {task(f, i).desc for f, i in tr + ind}
    test = fresh("pipeline", seen, 60, 10000) + fresh("reduce", seen, 60, 10000)
    pool = fresh("pipeline", seen, 150, 20000) + fresh("reduce", seen, 150, 20000) + [x for f in SMALL for x in [y for y in tr if y[0] == f][:24]]
    json.dump(test, open(os.path.join(OUT, "iid_test.json"), "w")); json.dump(pool, open(os.path.join(OUT, "ei_pool.json"), "w"))
    print("iid_test", len(test), "ei_pool", len(pool))


if __name__ == "__main__": main()
