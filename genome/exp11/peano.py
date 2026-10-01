"""exp11 probe B: the LAZY regime. Same expression search, but values are Peano naturals (0n / 1n+) and every
operator is lazy in the SupGen style (add/mul/min/max/monus by structural recursion, comparison against the expected
output one constructor at a time). Here a mismatch can be detected from a partial value, so a superposed choice whose
prefix already fails prunes the whole untouched sibling sub-search without materialising its candidates.
Leaves {x, 0..5}; binops {add, mul, min, max, monus}; N = 7, 252, 317,527.
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import random
from genome.exp11 import dsl
from genome.exp11.dsl import Labels, choice, run_hvm, show

CONSTS = list(range(6))
OPS = ["Add", "Mul", "Min", "Max", "Sub"]
PY = {"Add": lambda a, b: a + b, "Mul": lambda a, b: a * b, "Min": min, "Max": max, "Sub": lambda a, b: max(a - b, 0)}


def leaves(): return [("X",)] + [("K", k) for k in CONSTS]


def count(h): return 7 if h == 1 else 7 + len(OPS) * count(h - 1) ** 2


def ev(t, x):
    if t[0] == "X": return x
    if t[0] == "K": return t[1]
    return PY[t[0]](ev(t[1], x), ev(t[2], x))


def sample(h, rng):
    if h == 1: return rng.choice(leaves())
    c = count(h - 1)
    if rng.random() < 7 / count(h): return rng.choice(leaves())
    return (rng.choice(OPS), sample(h - 1, rng), sample(h - 1, rng))


def allc(h):
    if h == 1: return leaves()
    c = allc(h - 1)
    return leaves() + [(op, a, b) for op in OPS for a in c for b in c]


def hterm(t):
    if t[0] == "X": return "#X{}"
    if t[0] == "K": return f"#K{{{t[1]}n}}"
    return f"#{t[0]}{{{hterm(t[1])},{hterm(t[2])}}}"


def sup_term(h, lab=None):
    lab = lab or Labels()
    opts = [hterm(l) for l in leaves()]
    if h > 1: opts += [f"#{op}{{{sup_term(h - 1, lab)},{sup_term(h - 1, lab)}}}" for op in OPS]
    return choice(opts, lab)


SRC = """
@g = λ{ 0: λk. &{}; _: λc. λk. k }
@add = λ{ 0n: λb. b; 1n+: λp. λb. 1n+@add(p, b) }
@mul = λ{ 0n: λb. 0n; 1n+: λp. λ&b. @add(b, @mul(p, b)) }
@min = λ{ 0n: λb. 0n; 1n+: λp. λb. @min1(b, p) }
@min1 = λ{ 0n: λp. 0n; 1n+: λq. λp. 1n+@min(p, q) }
@max = λ{ 0n: λb. b; 1n+: λp. λb. @max1(b, p) }
@max1 = λ{ 0n: λp. 1n+p; 1n+: λq. λp. 1n+@max(p, q) }
@sub = λ{ 0n: λb. 0n; 1n+: λp. λb. @sub1(b, p) }
@sub1 = λ{ 0n: λp. 1n+p; 1n+: λq. λp. @sub(p, q) }
@eqn = λ{ 0n: λ{ 0n: 1; 1n+: λq. 0 }; 1n+: λp. λ{ 0n: 0; 1n+: λq. @eqn(p, q) } }
@ev = λ{
  #X: λx. x
  #K: λk. λx. k
  #Add: λl. λr. λ&x. @add(@ev(l, x), @ev(r, x))
  #Mul: λl. λr. λ&x. @mul(@ev(l, x), @ev(r, x))
  #Min: λl. λr. λ&x. @min(@ev(l, x), @ev(r, x))
  #Max: λl. λr. λ&x. @max(@ev(l, x), @ev(r, x))
  #Sub: λl. λr. λ&x. @sub(@ev(l, x), @ev(r, x))
}
@chk = λ{ []: λys. λp. p; <>: λx. λxs. λ{ <>: λy. λys. λ&p. @g(@eqn(@ev(p, x), y), @chk(xs, ys, p)); []: λp. &{} } }
"""


def nl(xs): return "[" + ",".join(f"{v}n" for v in xs) + "]"


def program(pterm, xs, ys): return SRC + f"@P = {pterm}\n@main = @chk({nl(xs)}, {nl(ys)}, @P)\n"


def parse(s):
    return _fix(dsl.parse(s.replace("n}", "}")))


def _fix(t):
    return t if t[0] in ("X", "K") else (t[0], _fix(t[1]), _fix(t[2]))


def oe_first(xs, ys, hmax):
    import time
    t0 = time.time(); tgt = tuple(ys); seen = {}; evals = 0
    for l in leaves():
        evals += 1; v = tuple(ev(l, x) for x in xs)
        if v == tgt: return l, time.time() - t0, evals
        seen.setdefault(v, l)
    old = {}
    for h in range(2, hmax + 1):
        prev = list(seen.items())
        for op in OPS:
            f = PY[op]
            for v1, e1 in prev:
                n1 = v1 not in old
                for v2, e2 in prev:
                    if not n1 and v2 in old: continue
                    evals += 1; v = tuple(f(a, b) for a, b in zip(v1, v2))
                    if v == tgt: return (op, e1, e2), time.time() - t0, evals
                    seen.setdefault(v, (op, e1, e2))
        old = dict(prev)
    return None, time.time() - t0, evals


def bench(name, h, tgt, n_sample=200, seed=0, xs=None):
    import json, os, statistics
    from concurrent.futures import ThreadPoolExecutor
    OUT = _REPO + "/runs/exp11"; HV = _REPO + "/genome/exp11/hvm4"
    _r = random.Random(1); xs = xs or [_r.randrange(8) for _ in range(8)]
    ys = [ev(tgt, x) for x in xs]; N = count(h)
    sup = run_hvm(program(sup_term(h), xs, ys), f"{HV}/{name}_sup.hvm")
    sols = [parse(s) for s in sup["sols"]]
    ok = all([ev(t, x) for x in xs] == ys for t in sols)
    rng = random.Random(seed)
    cands = [sample(h, rng) for _ in range(n_sample)] if N > n_sample else allc(h)
    os.makedirs(f"{OUT}/tmp", exist_ok=True)
    def one(ic):
        i, t = ic
        a = run_hvm(program(hterm(t), xs, ys), f"{OUT}/tmp/{name}_i{i}.hvm"); assert a["itrs"], a["err"]
        return a["itrs"]
    with ThreadPoolExecutor(3) as ex: ind = list(ex.map(one, enumerate(cands)))
    mi = statistics.mean(ind)
    nb = sum(1 for t in allc(h) if [ev(t, x) for x in xs] == ys) if N < 400_000 else None
    s, sec, evals = oe_first(xs, ys, h)
    r = {"config": name, "depth": h, "kind": "peano_map", "target": show(tgt), "xs": xs, "ys": ys, "n_candidates": N,
         "sup_itrs": sup["itrs"], "sup_wall": sup["wall"], "sup_heap": sup["heap"], "sup_survivors": len(sols),
         "sup_survivors_all_verified": ok, "brute_solutions": nb, "ind_n": len(cands), "ind_mean_itrs": mi,
         "ind_median_itrs": statistics.median(ind), "ind_extrap": mi * N, "gain": mi * N / sup["itrs"],
         "sup_itrs_per_cand": sup["itrs"] / N, "oe_first_solution": show(s) if s else None, "oe_first_sec": sec,
         "oe_first_vector_evals": evals, "sup_err": sup["err"][:300]}
    json.dump(r, open(f"{OUT}/{name}.json", "w"), indent=1)
    print(f"{name:<13} N={N:>9,} sup_itrs={sup['itrs']:>11,} ({r['sup_itrs_per_cand']:.1f}/cand, {sup['wall']:.2f}s) "
          f"ind={mi:.1f}/cand GAIN={r['gain']:.2f}x surv={len(sols)} brute={nb} verified={ok} | OE first: {r['oe_first_solution']} "
          f"in {sec * 1000:.1f}ms, {evals:,} vec-evals", flush=True)
    return r


PCFGS = {
    "peano_h1": (1, ("X",)),
    "peano_h2": (2, ("Mul", ("X",), ("K", 2))),
    "peano_h3a": (3, ("Add", ("Mul", ("X",), ("X",)), ("K", 1))),
    "peano_h3b": (3, ("Sub", ("Mul", ("X",), ("K", 3)), ("Min", ("X",), ("K", 4)))),
}

if __name__ == "__main__":
    import sys
    for n in sys.argv[1:]: bench(n, *PCFGS[n])
