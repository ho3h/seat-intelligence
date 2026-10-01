"""Unit-test every word template against its Python semantics through genome.verify, for several parameter settings.
   python -m genome.exp13.test_words [seed ...]      -> runs/exp13/word_tests.json
"""
from __future__ import annotations
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from genome.taskgen import _mk, L, SIZES_L, TEST_L, EDGE_L
from genome.types import u24
from genome.verify import verify
from genome.exp13.words import net_stage, net_reducer, stage_py, reducer_py, show

P_SAMPLES = [("gt", 5), ("gt", 50), ("lt", 10), ("lt", 500), ("ge", 3), ("ge", 100), ("even",), ("odd",), ("modeq", 3, 1), ("modeq", 7, 0)]
E_SAMPLES = [("lin", 3, 7), ("lin", 10, 100), ("xor", 255), ("xor", 7), ("and", 15), ("add", 9), ("sq",), ("mod", 6), ("div", 3),
             ("div", 10), ("ind", ("gt", 20)), ("ind", ("even",))]
STAGES = ([("map", e) for e in E_SAMPLES] + [("filter", p) for p in P_SAMPLES] + [("take", k) for k in (0, 1, 3, 8)]
          + [("drop", k) for k in (0, 1, 3, 8)] + [("reverse",), ("dedup",), ("runsum",), ("sort",), ("runmax",), ("runmin",), ("runxor",), ("diff",)])
REDUCERS = ([("sum",), ("count",), ("max",), ("min",), ("xor",), ("first",), ("last",), ("cntgtfirst",), ("argmax",)]
            + [(r, p) for r in ("idxfirst", "idxlast", "idxsum") for p in P_SAMPLES[:4] + [("even",), ("modeq", 3, 1)]])


def gen_for(hi):
    return lambda rng, n: [rng.randrange(hi) for _ in range(n)]


def program_for(term, is_red, hi=1000):
    f = reducer_py(term) if is_red else stage_py(term)
    return _mk(f"w13_{show(term)}", show(term), L, u24 if is_red else L, f, gen_for(hi), SIZES_L, TEST_L, EDGE_L)


def test_one(args):
    term, is_red, seeds = args
    net = net_reducer(term) if is_red else net_stage(term)
    out = {"term": show(term), "reducer": is_red, "results": []}
    for hi in (10, 1000):
        p = program_for(term, is_red, hi)
        for s in seeds:
            r = verify(p, net, seed=s, timeout=20.0, workers=1)
            out["results"].append({"hi": hi, "seed": s, "status": r["status"], "cex": r.get("counterexample") or r.get("reason"),
                                   "metrics": r.get("metrics")})
    out["pass"] = all(x["status"] == "pass" for x in out["results"])
    return out


def main(seeds):
    t0 = time.time()
    jobs = [(t, False, seeds) for t in STAGES] + [(t, True, seeds) for t in REDUCERS]
    with ThreadPoolExecutor(3) as ex: res = list(ex.map(test_one, jobs))
    for r in res:
        print(("PASS " if r["pass"] else "FAIL ") + r["term"] + ("" if r["pass"] else "  " + str([x["cex"] for x in r["results"] if x["status"] != "pass"][:1])))
    os.makedirs("runs/exp13", exist_ok=True)
    json.dump(res, open("runs/exp13/word_tests.json", "w"), indent=1, default=str)
    print(f"{sum(r['pass'] for r in res)}/{len(res)} word instances pass (seeds {seeds}, hi 10 and 1000), {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [0])
