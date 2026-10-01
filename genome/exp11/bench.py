"""exp11 bench: superposed search vs the same candidates evaluated independently vs the OE enumerator.

python -m genome.exp11.bench <config> [<config> ...]     (configs in CFGS; results -> runs/exp11/<config>.json)
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os, random, statistics, sys, time
from concurrent.futures import ThreadPoolExecutor
from genome.exp11 import dsl, baseline
from genome.exp11.dsl import count, sample, program, compiled_program, run_hvm, sup_term, parse, show, size

OUT = _REPO + "/runs/exp11"
HV = _REPO + "/genome/exp11/hvm4"
X, A = ("X",), ("A",)
K = lambda k: ("K", k)


def map_task(tgt, n=10, hi=64, seed=1):
    rng = random.Random(seed); xs = [rng.randrange(hi) for _ in range(n)]
    return {"kind": "map", "xs": xs, "ys": [dsl.ev(tgt, x) for x in xs]}


def fold_task(tgt, n=3, length=4, hi=10, z=0, seed=1):
    rng = random.Random(seed); xss = [[rng.randrange(hi) for _ in range(length)] for _ in range(n)]
    return {"kind": "fold", "z": z, "xss": xss, "ys": [dsl.fold(tgt, z, xs) for xs in xss]}


SMALL = ([1], [], ["Add", "Mul", "Xor"])        # leaves {x,1}, ops {+,*,xor}: N = 2, 14, 590, 1,044,302
CFGS = {
    # full DSL, map
    "map_h1": ("full", 1, "map", X),
    "map_h2": ("full", 2, "map", ("Mul", X, K(3))),
    "map_h3a": ("full", 3, "map", ("Add", ("Mod", 3, X), K(1))),
    "map_h3b": ("full", 3, "map", ("Xor", ("Mul", X, X), K(5))),
    "map_h3c": ("full", 3, "map", ("Min", ("Mul", X, K(2)), ("Add", X, K(5)))),
    # full DSL, fold bodies g(acc, x)
    "fold_h1": ("full", 1, "fold", X),
    "fold_h2": ("full", 2, "fold", ("Add", A, X)),
    "fold_h3a": ("full", 3, "fold", ("Add", A, ("Mul", X, X))),
    "fold_h3b": ("full", 3, "fold", ("Add", ("Mul", A, K(2)), X)),
    # small DSL depth-scaling series (map), depths 1..4
    "small_h1": ("small", 1, "map", X),
    "small_h2": ("small", 2, "map", ("Mul", X, X)),
    "small_h3": ("small", 3, "map", ("Add", ("Mul", X, X), K(1))),
    "small_h4": ("small", 4, "map", ("Xor", ("Mul", ("Add", X, K(1)), X), ("Add", X, X))),
    "smallfold_h3": ("small", 3, "fold", ("Add", ("Mul", A, X), K(1))),
}


def bench(name, n_sample=200, seed=0):
    dslname, h, kind, tgt = CFGS[name]
    dsl.set_dsl(*(SMALL if dslname == "small" else dsl.FULL))
    fold = kind == "fold"
    task = fold_task(tgt) if fold else map_task(tgt, hi=16 if dslname == "small" else 64)
    N = count(h, fold)
    res = {"config": name, "dsl": dslname, "depth": h, "kind": kind, "target": show(tgt), "task": task, "n_candidates": N}
    # 1. superposed search
    src = program(sup_term(h, fold), task)
    sup = run_hvm(src, f"{HV}/{name}_sup.hvm")
    sols = [parse(s) for s in sup["sols"]]
    ok = all(baseline._ok(t, task) for t in sols)
    res.update(sup_itrs=sup["itrs"], sup_wall=sup["wall"], sup_heap=sup["heap"], sup_survivors=len(sols),
               sup_survivors_all_verified=ok, sup_err=sup["err"][:500], sup_examples=[show(t) for t in sols[:5]])
    # 2. independent: same candidates one at a time (uniform sample over the exact candidate set)
    rng = random.Random(seed)
    cands = [sample(h, rng, fold) for _ in range(n_sample)] if N > n_sample else _all(h, fold)
    os.makedirs(f"{OUT}/tmp", exist_ok=True)
    def one(ic):
        i, t = ic
        a = run_hvm(program(dsl.hterm(t), task), f"{OUT}/tmp/{name}_i{i}.hvm")
        b = run_hvm(compiled_program(t, task), f"{OUT}/tmp/{name}_c{i}.hvm")
        assert a["itrs"] and b["itrs"], (a["err"], b["err"], t)
        return a["itrs"], b["itrs"], a["wall"], size(t)
    with ThreadPoolExecutor(3) as ex: ind = list(ex.map(one, enumerate(cands)))
    mi = statistics.mean(r[0] for r in ind); mc = statistics.mean(r[1] for r in ind)
    res.update(ind_n=len(cands), ind_mean_itrs=mi, ind_compiled_mean_itrs=mc, ind_mean_size=statistics.mean(r[3] for r in ind),
               ind_extrap=mi * N, ind_compiled_extrap=mc * N, gain=mi * N / sup["itrs"], gain_vs_compiled=mc * N / sup["itrs"],
               sup_itrs_per_cand=sup["itrs"] / N)
    # 3. OE enumerator
    s, sec, ev, ncls, chk = baseline.oe_first(task, h)
    res.update(oe_first_solution=show(s) if s else None, oe_first_sec=sec, oe_first_vector_evals=ev, oe_first_classes=ncls,
               oe_first_fold_checks=chk)
    if not fold:
        c = baseline.oe_count(task, h)
        res.update(oe_count_solutions=c["n_solutions"], oe_count_sec=c["sec"], oe_count_vector_evals=c["vector_evals"],
                   oe_count_classes_prev=c["classes_prev_level"], survivors_match_oe=c["n_solutions"] == len(sols))
    elif N <= 4_000_000:
        t0 = time.time(); nb = sum(1 for t in _all(h, fold) if baseline._ok(t, task))
        res.update(brute_solutions=nb, brute_sec=time.time() - t0, survivors_match_brute=nb == len(sols))
    json.dump(res, open(f"{OUT}/{name}.json", "w"), indent=1)
    return res


def _all(h, fold):
    if h == 1: return dsl.leaves(fold)
    c = _all(h - 1, fold)
    return dsl.leaves(fold) + [("Mod", m, a) for m in dsl.MODS for a in c] + [(op, a, b) for op in dsl.BINOPS for a in c for b in c]


def line(r):
    s = (f"{r['config']:<13} N={r['n_candidates']:>11,} sup_itrs={r['sup_itrs']:>12,} ({r['sup_itrs_per_cand']:.1f}/cand, {r['sup_wall']:.2f}s) "
         f"ind={r['ind_mean_itrs']:.1f}/cand compiled={r['ind_compiled_mean_itrs']:.1f}/cand  GAIN={r['gain']:.2f}x "
         f"(vs compiled {r['gain_vs_compiled']:.2f}x) surv={r['sup_survivors']} verified={r['sup_survivors_all_verified']}")
    if "oe_count_solutions" in r: s += f" oe_count={r['oe_count_solutions']}"
    if "brute_solutions" in r: s += f" brute={r['brute_solutions']}"
    s += f" | OE first: {r['oe_first_solution']} in {r['oe_first_sec'] * 1000:.1f}ms, {r['oe_first_vector_evals']:,} vec-evals"
    return s


if __name__ == "__main__":
    for n in sys.argv[1:]:
        r = bench(n); print(line(r), flush=True)


def se(name, n=1000, seed=7):
    """Larger fresh sample for the depth-3 independent means: mean, standard error, 95% CI of the gain."""
    dslname, h, kind, tgt = CFGS[name]
    dsl.set_dsl(*(SMALL if dslname == "small" else dsl.FULL))
    fold = kind == "fold"
    task = fold_task(tgt) if fold else map_task(tgt, hi=16 if dslname == "small" else 64)
    rng = random.Random(seed); cands = [sample(h, rng, fold) for _ in range(n)]
    def one(ic):
        i, t = ic
        a = run_hvm(program(dsl.hterm(t), task), f"{OUT}/tmp/{name}_se_i{i}.hvm")
        b = run_hvm(compiled_program(t, task), f"{OUT}/tmp/{name}_se_c{i}.hvm")
        os.remove(f"{OUT}/tmp/{name}_se_i{i}.hvm"); os.remove(f"{OUT}/tmp/{name}_se_c{i}.hvm")
        return a["itrs"], b["itrs"]
    with ThreadPoolExecutor(3) as ex: ind = list(ex.map(one, enumerate(cands)))
    res = json.load(open(f"{OUT}/{name}.json")); N = res["n_candidates"]; S = res["sup_itrs"]
    for j, key in ((0, "interp"), (1, "compiled")):
        xs = [r[j] for r in ind]; m = statistics.mean(xs); e = statistics.stdev(xs) / len(xs) ** 0.5
        res[f"se{n}_{key}"] = {"mean": m, "se": e, "gain": m * N / S, "gain_ci95": [(m - 1.96 * e) * N / S, (m + 1.96 * e) * N / S]}
        print(f"{name} n={n} {key}: {m:.1f}+-{e:.1f}/cand gain {m * N / S:.2f}x CI95 [{(m - 1.96 * e) * N / S:.2f}, {(m + 1.96 * e) * N / S:.2f}]", flush=True)
    json.dump(res, open(f"{OUT}/{name}.json", "w"), indent=1)
