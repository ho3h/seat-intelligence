"""Construction gate for the benchmark (NOT the experiment): every fold's nets must agree with its Python models, and its
original sequential net must pass genome.verify seeds 0-2 against the list program. Membership and labels are not touched
by this stage; an authoring error is fixed in folds.py, an unfixable fold would be reported as excluded."""
from __future__ import annotations
import json, random, sys, itertools
from concurrent.futures import ThreadPoolExecutor
from ..verify import verify
from . import folds as F
from .tester import _drive
from .nets import seq_net
from .programs import list_program


def crosscheck(f, n=400, seed=1):
    rng = random.Random(seed)
    # reachable-ish states from python model
    def rl(): return [f.gen(rng) for _ in range(rng.randrange(0, 12))]
    states = [f.state_of(rl()) for _ in range(n)]
    xs = [f.gen(rng) for _ in range(n)]
    S = f.state_t
    errs = []
    # comb
    items = [(rng.choice(states), rng.choice(states)) for _ in range(n)]
    res = _drive(f, [S, S], [S], "  & @comb ~ (v0 (v1 o))", ["o"], items)
    for it, r in zip(items, res):
        if r != f.py_comb(*it): errs.append(("comb", it, r, f.py_comb(*it))); break
    # lift
    res = _drive(f, [f.elem_t], [S], "  & @lift ~ (v0 o)", ["o"], xs)
    for x, r in zip(xs, res):
        if r != f.py_lift(x): errs.append(("lift", x, r, f.py_lift(x))); break
    # step
    items = [(rng.choice(states), x) for x in xs]
    res = _drive(f, [S, f.elem_t], [S], "  & @step ~ (v0 (v1 o))", ["o"], items)
    for it, r in zip(items, res):
        if r != f.step_py(*it): errs.append(("step", it, r, f.step_py(*it))); break
    # fin
    if f.fin_txt:
        res = _drive(f, [S], [f.out_t], "  & @fin ~ (v0 o)", ["o"], states)
        for s, r in zip(states, res):
            if r != f.py_fin(s): errs.append(("fin", s, r, f.py_fin(s))); break
    return errs


def one(f):
    out = {"fold": f.id, "label": f.label}
    try:
        out["crosscheck"] = crosscheck(f)
    except Exception as e:
        out["crosscheck"] = [("exception", str(e)[:300])]
    p = list_program(f)
    net = seq_net(f)
    out["verify"] = []
    for seed in (0, 1, 2):
        r = verify(p, net, seed, workers=3)
        out["verify"].append({"seed": seed, "status": r["status"], "failed": r.get("failed"), "cex": r.get("counterexample"), "reason": r.get("reason")})
    return out


if __name__ == "__main__":
    ids = sys.argv[1:]
    fs = [f for f in F.FOLDS if not ids or f.id in ids]
    res = []
    with ThreadPoolExecutor(2) as ex:
        for out in ex.map(one, fs):
            ok = not out["crosscheck"] and all(v["status"] == "pass" for v in out["verify"])
            print(("OK  " if ok else "BAD ") + out["fold"], "" if ok else json.dumps(out, default=str)[:600], flush=True)
            res.append(out)
    json.dump(res, open("runs/hero3/construct.json", "w"), default=str, indent=1)
