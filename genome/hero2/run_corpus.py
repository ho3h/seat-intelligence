"""Run the normalizer over the frozen corpus. usage: python3 -m genome.hero2.run_corpus OUT.json [class-prefix ...]"""
import json, sys, time, hashlib
from genome.hero2 import corpus as C
from genome.hero2.prove import Prover


def main():
    out = sys.argv[1]
    only = sys.argv[2:]
    cases = C.all_cases()
    res = {}
    for c in cases:
        if only and not any(c.cls.startswith(o) for o in only): continue
        t0 = time.time()
        try:
            v = Prover(c.A, c.B).prove()
            r = {"equal": v.equal, "tier": v.tier, "reason": v.reason, "stats": v.stats}
        except Exception as e:
            import traceback
            r = {"equal": False, "tier": None, "reason": "EXCEPTION " + repr(e)[:200], "stats": {}}
            traceback.print_exc()
        r.update(cls=c.cls, expect=c.expect, denom=c.denom, secs=round(time.time() - t0, 2))
        res[c.id] = r
        print(f"{c.id:45s} {c.expect:8s} proved={str(r['equal']):5s} tier={r['tier']} {r['secs']:6.2f}s  {r['reason'][:70]}", flush=True)
    json.dump({"corpus_sha256": hashlib.sha256(open(C.__file__, "rb").read()).hexdigest(), "results": res}, open(out, "w"), indent=1)


main()
