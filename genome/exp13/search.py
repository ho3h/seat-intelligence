"""exp13 search: bottom-up enumeration with observational-equivalence (OE) merging over stage sequences, from input/output
examples only (no description). A state is the tuple of the example lists after some stages; two stage sequences that
give the same state are one class (the first, simplest, is kept). Breadth-first in the number of stages, so the first
solution found has the fewest stages; within a level, stages are tried in a fixed simplicity order (parameterless words,
then small/round constants first).

List outputs: up to 3 stages. Every stage is length non-increasing, so a state shorter than the target is pruned. The last
stage is filled deductively: length-preserving words only if lengths already match (maps looked up through a per-input
value index: E(x0) == y0), length-reducing words only if they do not (take/drop k solved from the lengths).
Number outputs: up to 2 stages + a reducer (3 stages + reducer only within the time budget); index reducers (idxfirst,
idxlast, idxsum over a predicate hole) only after <= 1 stage, filled through per-value predicate bitmasks.
"""
from __future__ import annotations
import time
from functools import reduce as _reduce
from genome.exp13.words import M, BIG, pred_py, expr_py

# ------------------------------------------------------------------ hole grids (a generic "small / round constants" prior,
# wider than taskgen's own constants; see docs/WORD-FILLING.md)
KS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16, 20, 25, 30, 32, 40, 50, 60, 64, 75, 100, 128, 150, 200, 250, 256, 300, 400, 500, 512, 750, 1000]
MODS = list(range(2, 13))
PREDS = ([("even",), ("odd",)] + [(c, k) for k in KS for c in ("gt", "lt", "ge") if not (c == "ge" and k == 0) and not (c == "lt" and k == 0)]
         + [("modeq", m, r) for m in MODS for r in range(m) if not (m == 2)])
MULS = list(range(2, 11)); ADDS_B = [0, 1, 2, 3, 4, 5, 7, 10, 100]; MASKS = [1, 3, 7, 15, 31, 63, 127, 255]
ADDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
EXPRS = ([("sq",)] + [("add", c) for c in ADDS] + [("lin", a, b) for b in ADDS_B for a in MULS]
         + [("xor", m) for m in MASKS] + [("and", m) for m in MASKS] + [("mod", m) for m in MODS] + [("div", a) for a in MULS]
         + [("ind", p) for p in PREDS])
TAKES = list(range(1, 11))


def _t_dedup(xs): return tuple(x for i, x in enumerate(xs) if i == 0 or xs[i - 1] != x)
def _runop(xs, f):
    out = []
    for x in xs: out.append(x if not out else f(out[-1], x))
    return tuple(out)


PRESERVE = [(("reverse",), lambda xs: xs[::-1]), (("sort",), lambda xs: tuple(sorted(xs))),
            (("runsum",), lambda xs: _runop(xs, lambda a, b: (a + b) % M)), (("runmax",), lambda xs: _runop(xs, max)),
            (("runmin",), lambda xs: _runop(xs, min)), (("runxor",), lambda xs: _runop(xs, lambda a, b: a ^ b))]
REDUCE_FIXED = [(("dedup",), _t_dedup), (("diff",), lambda xs: tuple((xs[i + 1] - xs[i]) % M for i in range(len(xs) - 1)))]


def _mk_map(E):
    f = expr_py(E); return lambda xs: tuple(f(x) for x in xs)
def _mk_filter(P):
    f = pred_py(P); return lambda xs: tuple(x for x in xs if f(x))


MAPS = [(("map", E), _mk_map(E)) for E in EXPRS]
FILTERS = [(("filter", P), _mk_filter(P)) for P in PREDS]
TAKEDROP = [(("take", k), (lambda xs, k=k: xs[:k])) for k in TAKES] + [(("drop", k), (lambda xs, k=k: xs[k:])) for k in TAKES]
STAGES = PRESERVE + REDUCE_FIXED + TAKEDROP + FILTERS + MAPS          # expansion order = simplicity order

PLAIN_RED = [(("sum",), lambda xs: sum(xs) % M), (("count",), len), (("max",), lambda xs: max(xs, default=0)),
             (("min",), lambda xs: min(xs, default=BIG)), (("xor",), lambda xs: _reduce(lambda a, b: a ^ b, xs, 0)),
             (("first",), lambda xs: xs[0] if xs else 0), (("last",), lambda xs: xs[-1] if xs else 0),
             (("cntgtfirst",), lambda xs: sum(1 for x in xs[1:] if x > xs[0]) if xs else 0),
             (("argmax",), lambda xs: xs.index(max(xs)) if xs else 0)]
_PF = [pred_py(p) for p in PREDS]
_EF = [expr_py(e) for e in EXPRS]
ALLP = (1 << len(PREDS)) - 1


class Index:
    """Per-value caches: predicate bitmask of x, and {E(x): [expr ids]}."""
    def __init__(self): self.pm = {}; self.em = {}
    def pmask(self, x):
        m = self.pm.get(x)
        if m is None:
            m = 0
            for i, f in enumerate(_PF):
                if f(x): m |= 1 << i
            self.pm[x] = m
        return m
    def maps_to(self, x, y):
        d = self.em.get(x)
        if d is None:
            d = {}
            for i, f in enumerate(_EF): d.setdefault(f(x), []).append(i)
            self.em[x] = d
        return d.get(y, ())


def _bits(m):
    while m:
        b = m & -m; yield b.bit_length() - 1; m ^= b


def idx_reducers(state, ys, ix):
    """(word, pred) consistent with all examples, via bitmasks. Yields reducer terms."""
    for kind in ("idxfirst", "idxlast"):
        cand = ALLP
        for xs, y in zip(state, ys):
            masks = [ix.pmask(x) for x in xs]
            if y == BIG:
                for m in masks: cand &= ~m
            elif y < len(xs):
                cand &= masks[y]
                rng = masks[:y] if kind == "idxfirst" else masks[y + 1:]
                for m in rng: cand &= ~m
            else: cand = 0
            if not cand: break
        for b in _bits(cand): yield (kind, PREDS[b])
    # idxsum: per predicate (only preds that survive a cheap first-example check)
    cand = []
    xs0, y0 = state[0], ys[0]
    masks0 = [ix.pmask(x) for x in xs0]
    for b in range(len(PREDS)):
        if sum(i for i, m in enumerate(masks0) if m >> b & 1) % M == y0: cand.append(b)
    for b in cand:
        ok = True
        for xs, y in zip(state[1:], ys[1:]):
            if sum(i for i, x in enumerate(xs) if ix.pmask(x) >> b & 1) % M != y: ok = False; break
        if ok: yield ("idxsum", PREDS[b])


def last_stage_list(state, ys, ix):
    """All final stages S with S(state) == ys (lists)."""
    same = all(len(a) == len(b) for a, b in zip(state, ys))
    out = []
    if same:
        for S, f in PRESERVE:
            if all(f(a) == b for a, b in zip(state, ys)): out.append(S)
        # maps via value index on the first element of the first non-empty example
        ne = [(a, b) for a, b in zip(state, ys) if a]
        if ne:
            cand = ix.maps_to(ne[0][0][0], ne[0][1][0])
            for i in cand:
                f = _EF[i]
                if all(f(x) == y for a, b in ne for x, y in zip(a, b)): out.append(("map", EXPRS[i]))
        return out
    if any(len(a) < len(b) for a, b in zip(state, ys)): return out
    for S, f in REDUCE_FIXED:
        if all(f(a) == b for a, b in zip(state, ys)): out.append(S)
    for S, f in TAKEDROP:
        if all(f(a) == b for a, b in zip(state, ys)): out.append(S)
    # filters: equal values share a fate, so P must hold on every value of b and fail on every other value of a
    cand = ALLP
    for a, b in zip(state, ys):
        kept = set(b)
        if not kept <= set(a): return out
        for x in set(a): cand &= ix.pmask(x) if x in kept else ~ix.pmask(x)
        if not cand: return out
    for bit in _bits(cand):
        f = _PF[bit]
        if all(tuple(x for x in a if f(x)) == b for a, b in zip(state, ys)): out.append(("filter", PREDS[bit]))
    return out


def search(examples, out_is_list, max_stages=3, budget=60.0, idx_max_stages=1):
    """examples: [(input list, output)]. Returns dict(stages, reducer, sec, states, found)."""
    t0 = time.time(); ix = Index()
    xs = tuple(tuple(e[0]) for e in examples)
    ys = tuple(tuple(e[1]) for e in examples) if out_is_list else tuple(e[1] for e in examples)
    level = {xs: ()}; seen = {xs}; n_states = 1

    def check(state, prog, d):
        if out_is_list:
            return (prog, None) if state == ys else None
        for R, f in PLAIN_RED:
            if all(f(s) == y for s, y in zip(state, ys)): return prog, R
        if d <= idx_max_stages:
            for R in idx_reducers(state, ys, ix): return prog, R
        return None

    def done(prog, R, timeout=False):
        return {"found": prog is not None, "stages": list(prog) if prog is not None else None, "reducer": R,
                "sec": time.time() - t0, "states": n_states, "timeout": timeout}

    for st, prog in level.items():
        r = check(st, prog, 0)
        if r: return done(*r)
    for d in range(1, max_stages + 1):
        last = out_is_list and d == max_stages
        if last:  # deductive final stage, nothing stored
            for st, prog in level.items():
                if time.time() - t0 > budget: return done(None, None, True)
                ss = last_stage_list(st, ys, ix)
                if ss: return done(prog + (ss[0],), None)
            break
        new = {}
        for st, prog in level.items():
            if time.time() - t0 > budget: return done(None, None, True)
            for S, f in STAGES:
                ns = tuple(f(s) for s in st)
                if ns in seen: continue
                seen.add(ns)
                if out_is_list and any(len(a) < len(b) for a, b in zip(ns, ys)): continue
                new[ns] = prog + (S,); n_states += 1
                r = check(ns, new[ns], d)
                if r: return done(*r)
        level = new
    return done(None, None)
