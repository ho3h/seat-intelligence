"""Kill rule (iii): for every pair the normalizer proved, sample concrete inputs through the real executor and look for a disagreement.
usage: python3 -m genome.hero2.soundness RUN.json OUT.json [n_syn] [n_real]"""
import json, sys, time
from genome.hero2 import corpus as C
from genome.hero2.harness import sample_pair


def main():
    run = json.load(open(sys.argv[1]))["results"]
    out = sys.argv[2]
    n_syn = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    n_real = int(sys.argv[4]) if len(sys.argv) > 4 else 250
    cases = {c.id: c for c in C.all_cases()}
    res = {}
    t0 = time.time()
    for cid, r in run.items():
        if not r["equal"]: continue
        c = cases[cid]
        s = sample_pair(c, n_real if c.prog is not None else n_syn, seed=9000, workers=4)
        res[cid] = {"tier": r["tier"], "expect": c.expect, **s}
        print(f"{cid:45s} tier={r['tier']:4s} n={s['n']:3d} agree={s['agree']:3d} disagree={s['disagree']} batched={s['batched']}", flush=True)
    json.dump(res, open(out, "w"), indent=1)
    bad = [k for k, v in res.items() if v["disagree"]]
    print("proved pairs sampled:", len(res), "with disagreement:", bad, "min n:", min(v["n"] for v in res.values()), f"{time.time()-t0:.0f}s")

main()
