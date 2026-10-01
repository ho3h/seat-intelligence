"""exp11: BATCHED independent baseline. The same sampled candidates, evaluated one after another inside ONE HVM4 run
(no superposition), so fixed per-run setup (parsing, building the example lists) is not charged to every candidate.
Marginal cost per candidate = (itrs(batch of n) - itrs(batch of 0)) / n. Interpreted (@ev over the AST) and compiled
(each candidate a direct HVM lambda) variants. Same early exit on the first mismatching element / example.
   python -m genome.exp11.batched <config> ...   (configs from bench.CFGS; adds fields to runs/exp11/<config>.json)
"""
import json, random, sys
from genome.exp11 import dsl, bench
from genome.exp11.dsl import PRELUDE, _evcases, cterm, hterm, hl, run_hvm, sample, count

OKMAP = """
@ok = λ{ []: λys. λp. 1; <>: λx. λxs. λ{ <>: λy. λys. λ&p. @k((@E(p, x) == y), xs, ys, p); []: λp. 0 } }
@k = λ{ 0: λxs. λys. λp. 0; _: λc. λxs. λys. λp. @ok(xs, ys, p) }
"""
OKFOLD = """
@fold = λ{ []: λacc. λp. acc; <>: λx. λxs. λacc. λ&p. @fold(xs, @E(p, acc, x), p) }
@ok = λ{ []: λys. λp. 1; <>: λxs. λxss. λ{ <>: λy. λys. λ&p. @k((@fold(xs, Z, p) == y), xss, ys, p); []: λp. 0 } }
@k = λ{ 0: λxs. λys. λp. 0; _: λc. λxs. λys. λp. @ok(xs, ys, p) }
"""


def src(cands, task, compiled):
    fold = task["kind"] == "fold"
    if compiled:
        E = "@E = λf. f\n" if not fold else "@E = λf. f\n"
        items = [(f"λ&a. λ&x. {cterm(t, True)}" if fold else f"λ&x. {cterm(t)}") for t in cands]
        # λ&x with 0/1 uses is fine for HVM4 autodup (erases / passes through)
    else:
        E = "@E = @ev\n"; items = [hterm(t) for t in cands]
    body = (OKFOLD.replace("Z", str(task["z"])) if fold else OKMAP)
    data = hl(task["xs"]) + ", " + hl(task["ys"]) if not fold else "[" + ",".join(hl(x) for x in task["xss"]) + "], " + hl(task["ys"])
    run = "@run = λ{ []: 0; <>: λp. λps. (@ok(" + data + ", p) + @run(ps)) }\n"
    return PRELUDE + _evcases(fold) + E + body + run + "@main = @run([" + ",".join(items) + "])\n"


def measure(name, n=200, seed=0):
    dslname, h, kind, tgt = bench.CFGS[name]
    dsl.set_dsl(*(bench.SMALL if dslname == "small" else dsl.FULL))
    fold = kind == "fold"
    task = bench.fold_task(tgt) if fold else bench.map_task(tgt, hi=16 if dslname == "small" else 64)
    rng = random.Random(seed); cands = [sample(h, rng, fold) for _ in range(n)]   # same sample as bench.py
    out = {}
    for comp in (False, True):
        r0 = run_hvm(src([], task, comp), f"{bench.OUT}/tmp/{name}_b0.hvm")
        r1 = run_hvm(src(cands, task, comp), f"{bench.OUT}/tmp/{name}_b{n}.hvm")
        assert r0["itrs"] and r1["itrs"], (r0["err"], r1["err"])
        out["compiled" if comp else "interp"] = (r1["itrs"] - r0["itrs"]) / n
    res = json.load(open(f"{bench.OUT}/{name}.json"))
    N = res["n_candidates"]
    res.update(batched_interp_per_cand=out["interp"], batched_compiled_per_cand=out["compiled"],
               gain_vs_batched_interp=out["interp"] * N / res["sup_itrs"], gain_vs_batched_compiled=out["compiled"] * N / res["sup_itrs"])
    json.dump(res, open(f"{bench.OUT}/{name}.json", "w"), indent=1)
    print(f"{name:<13} sup={res['sup_itrs_per_cand']:.1f}/cand batched interp={out['interp']:.1f} compiled={out['compiled']:.1f} "
          f"-> gain vs batched interp {res['gain_vs_batched_interp']:.2f}x, vs batched compiled {res['gain_vs_batched_compiled']:.2f}x", flush=True)


if __name__ == "__main__":
    for nm in sys.argv[1:]: measure(nm)
