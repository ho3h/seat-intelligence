"""exp11 strong baseline: bottom-up enumeration with observational-equivalence (OE) merging, same DSL, same examples.

oe_first : classic pure-Python OE enumerator (one expression per distinct output vector; a new pair is built only if
           at least one child is new at the previous height). Stops at the first solution. Counts vector evaluations.
oe_count : numpy version that carries, per class, the exact number of DSL expressions in it, so the number of ALL
           solutions of height <= h is exact (checks the superposed search's survivor count without enumerating).
Fold bodies g(acc,x): OE on a probe grid (acc in 0..GRID-1, x in the example values). Unsound in general (two bodies
equal on the grid may differ on reached states); every reported solution is verified by the real fold, and the
solution count is compared with the superposed search's exact survivors.
"""
from __future__ import annotations
import time
import numpy as np
from genome.exp11 import dsl
from genome.exp11.dsl import U, PYOP

GRID = 32


def _npop(op, a, b):
    if op == "Add": return (a + b) & U
    if op == "Sub": return (a - b) & U
    if op == "Mul": return (a * b) & U
    if op == "Xor": return a ^ b
    if op == "And": return a & b
    if op == "Min": return np.minimum(a, b)
    if op == "Max": return np.maximum(a, b)
    if op == "Lt": return (a < b).astype(np.uint64)
    if op == "Eq": return (a == b).astype(np.uint64)


def _probe(task):
    if task["kind"] == "map":
        return [(x, 0) for x in task["xs"]]
    xv = sorted({x for xs in task["xss"] for x in xs})
    return [(x, a) for a in range(GRID) for x in xv]


def _ok(t, task):
    if task["kind"] == "map": return all(dsl.ev(t, x) == y for x, y in zip(task["xs"], task["ys"]))
    return all(dsl.fold(t, task["z"], xs) == y for xs, y in zip(task["xss"], task["ys"]))


def oe_first(task, hmax):
    """Pure Python classic OE. Returns (solution expr or None, seconds, vector evaluations, classes, fold checks)."""
    t0 = time.time(); pr = _probe(task); fold = task["kind"] == "fold"
    target = tuple(task["ys"]) if not fold else None
    evals = checks = 0
    seen = {}
    def add(v, e):
        nonlocal checks
        if v in seen: return None
        seen[v] = e
        if not fold: return e if v == target else None
        checks += 1
        return e if _ok(e, task) else None
    for l in dsl.leaves(fold):
        evals += 1
        s = add(tuple(dsl.ev(l, x, a) for x, a in pr), l)
        if s: return s, time.time() - t0, evals, len(seen), checks
    old = {}                        # classes of height <= h-2
    for h in range(2, hmax + 1):
        prev = list(seen.items()); new_prev = [(v, e) for v, e in prev if v not in old]
        for m in dsl.MODS:
            for v, e in new_prev:
                evals += 1
                s = add(tuple(a % m for a in v), ("Mod", m, e))
                if s: return s, time.time() - t0, evals, len(seen), checks
        for op in dsl.BINOPS:
            f = PYOP[op]
            for v1, e1 in prev:
                n1 = v1 not in old
                for v2, e2 in prev:
                    if not n1 and v2 in old: continue
                    evals += 1
                    s = add(tuple(f(a, b) for a, b in zip(v1, v2)), (op, e1, e2))
                    if s: return s, time.time() - t0, evals, len(seen), checks
        old = dict(prev)
    return None, time.time() - t0, evals, len(seen), checks


def oe_count(task, hmax):
    """Map tasks: exact number of expressions of height <= hmax solving the task, via per-class expression counts.
    Final level is hashed per block (no vectors kept), so hmax=4 of a small DSL fits in memory."""
    assert task["kind"] == "map"
    t0 = time.time()
    xs = np.array(task["xs"], dtype=np.uint64); tgt = np.array(task["ys"], dtype=np.uint64)
    ls = dsl.leaves(False)
    def leafvec(l): return xs.copy() if l[0] == "X" else np.full(len(xs), l[1], dtype=np.uint64)
    V = np.stack([leafvec(l) for l in ls]); C = np.ones(len(ls), dtype=np.int64); R = list(ls)
    V, C, R = _merge(V, C, R)
    nsol = 0; reps = []; evals = 0
    for h in range(2, hmax + 1):
        D = len(V); last = h == hmax
        blocks = [(np.stack([leafvec(l) for l in ls]), np.ones(len(ls), dtype=np.int64), (lambda i: ls[i]))]
        for m in dsl.MODS:
            blocks.append((V % np.uint64(m), C, (lambda i, m=m: ("Mod", m, R[i]))))
        for op in dsl.BINOPS:
            blocks.append((None, (C[:, None] * C[None, :]).reshape(-1), (lambda i, op=op: (op, R[i // D], R[i % D]))))
        if last:
            for bi, (bv, bc, rf) in enumerate(blocks):
                if bv is None:
                    op = dsl.BINOPS[bi - 1 - len(dsl.MODS)]
                    bv = _npop(op, V[:, None, :], V[None, :, :]).reshape(D * D, -1)
                evals += len(bc)
                mask = np.all(bv == tgt, axis=1); idx = np.nonzero(mask)[0]
                nsol += int(bc[idx].sum()); reps += [dsl.show(rf(int(i))) for i in idx[:3]]
                del bv
            ncls = None
        else:
            vs, cs, rs = [], [], []
            for bi, (bv, bc, rf) in enumerate(blocks):
                if bv is None:
                    op = dsl.BINOPS[bi - 1 - len(dsl.MODS)]
                    bv = _npop(op, V[:, None, :], V[None, :, :]).reshape(D * D, -1)
                vs.append(bv); cs.append(bc); rs.append((len(bc), rf)); evals += len(bc)
            V, C, R = _merge(np.concatenate(vs), np.concatenate(cs), rs)
            ncls = len(V)
    if hmax == 1:
        mask = np.all(V == tgt, axis=1); nsol = int(C[mask].sum()); reps = [dsl.show(R[i]) for i in np.nonzero(mask)[0]]
    return {"n_solutions": nsol, "classes_prev_level": len(V), "vector_evals": evals, "reps": reps[:10], "sec": time.time() - t0}


def _merge(V, C, R):
    """R: list of exprs, or list of (block_len, index->expr) segments."""
    u, first, inv = np.unique(V, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    cnt = np.zeros(len(u), dtype=np.int64); np.add.at(cnt, inv, C)
    if R and isinstance(R[0], tuple) and len(R[0]) == 2 and callable(R[0][1]):
        offs = np.cumsum([0] + [n for n, _ in R])
        def get(g):
            b = int(np.searchsorted(offs, g, side="right") - 1); return R[b][1](int(g - offs[b]))
        reps = [get(g) for g in first]
    else:
        reps = [R[i] for i in first]
    return u, cnt, reps
