"""Builds fixed, validated task sets from the generator and writes manifests (family, index) to data/tasksets/.
   python -m genome.taskset build
"""
import copy, json, os, random, sys, time
from .taskgen import FAMILIES, TRAIN_FAMILIES, HOLDOUT_FAMILIES, task
from .types import encode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "tasksets")
BOOL_LIKE = ()


def valid(p) -> bool:
    rng = random.Random(5); outs = set()
    inputs = [e for e in p.edges] + [p.gen(rng, n) for n in p.sizes + p.test_sizes for _ in range(4)]
    for x in inputs:
        if p.pre and not p.pre(x): continue
        snap = copy.deepcopy(x); t0 = time.time(); y = p.ref(x)
        if x != snap or time.time() - t0 > 2.0: return False
        encode(x, p.inp); encode(y, p.out); outs.add(repr(y))
    return len(outs) >= 4


def build(per_family_train=250, per_family_hold=30, tries=4000):
    os.makedirs(OUT, exist_ok=True)
    seen = set(); sets = {"train": [], "holdout": []}
    for split, fams, want in (("train", TRAIN_FAMILIES, per_family_train), ("holdout", HOLDOUT_FAMILIES, per_family_hold)):
        for fam in fams:
            got = 0
            for i in range(tries):
                if got >= want: break
                p = task(fam, i)
                if p.desc in seen: continue
                try: ok = valid(p)
                except Exception: ok = False
                if not ok: continue
                seen.add(p.desc); sets[split].append([fam, i]); got += 1
            print(f"{split:8s} {fam:12s} {got}/{want}")
    for k, v in sets.items(): json.dump(v, open(os.path.join(OUT, f"{k}.json"), "w"))
    print({k: len(v) for k, v in sets.items()})


def load(split):
    return [task(f, i) for f, i in json.load(open(os.path.join(OUT, f"{split}.json")))]


if __name__ == "__main__" and sys.argv[1:] == ["build"]: build()
