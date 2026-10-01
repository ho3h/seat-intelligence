"""Sampling harness: run both nets of a Case on concrete inputs through the REAL HVM2 executor and compare results.
Used for (1) ground-truth validation of the corpus labels, (2) the soundness sampling of every proved pair (kill rule iii)."""
from __future__ import annotations
import random, re
from concurrent.futures import ThreadPoolExecutor
from genome.executor import run_net
from genome.types import encode, U24, List, Tup

EDGE_NUMS = [0, 1, 2, 3, 4, 5, 7, 999, 1000, 16777214, 16777215]


def gen_num(rng):
    r = rng.random()
    if r < 0.40: return rng.randrange(0, 9)
    if r < 0.60: return rng.choice(EDGE_NUMS)
    return rng.randrange(0, 1 << 24)


def gen_value(t, rng):
    if isinstance(t, U24): return gen_num(rng)
    if isinstance(t, List):
        n = rng.choice([0, 0, 1, 1, 2, 3, 3, 4, 5, 6, 7, 9])
        return [gen_value(t.elem, rng) for _ in range(n)]
    if isinstance(t, Tup): return tuple(gen_value(e, rng) for e in t.elems)
    raise TypeError(t)


def edge_values(t):
    if isinstance(t, U24): return list(EDGE_NUMS)
    if isinstance(t, List): return [[], [0], [16777215], [1, 2, 3], [5, 0, 7], [4, 5, 6, 7, 8, 9, 10]]
    if isinstance(t, Tup):
        base = [tuple(e) for e in zip(*[[v for v in edge_values(x)][:6] for x in t.elems])]
        return base
    return []


def norm_result(text: str) -> str:
    """alpha-normalise variable names in an executor result so that two isomorphic outputs compare equal"""
    names = {}
    def sub(m):
        w = m.group(0)
        if w not in names: names[w] = f"v{len(names)}"
        return names[w]
    return re.sub(r"(?<![\w@])[A-Za-z_][A-Za-z_0-9]*", sub, text)


def synth_inputs(case, n, seed):
    rng = random.Random(f"{case.id}|{seed}")
    vals = list(edge_values(case.inp))
    while len(vals) < n: vals.append(gen_value(case.inp, rng))
    return vals[:max(n, len(edge_values(case.inp)))]


def real_inputs(case, n, seed):
    from genome.verify import build_cases
    p = case.prog
    vals = []
    s = seed
    while len(vals) < n and s < seed + 8:
        for kind, sz, x in build_cases(p, s):
            if kind == "big": continue
            vals.append(x)
        s += 1
    rng = random.Random(f"{case.id}|{seed}")
    rng.shuffle(vals)
    return vals[:n]


def inputs_for(case, n, seed):
    return synth_inputs(case, n, seed) if case.inp is not None else real_inputs(case, n, seed)


def assemble_side(case, book: str, value) -> str:
    t = case.inp if case.inp is not None else case.prog.inp
    root, defs = encode(value, t)
    return f"@main = r\n  & @prog ~ ({root} r)\n\n" + "\n".join(defs) + "\n\n" + book + "\n"


def run_both(case, value, timeout=20.0):
    ra = run_net(assemble_side(case, case.A, value), "run", timeout)
    rb = run_net(assemble_side(case, case.B, value), "run", timeout)
    return ra, rb


def _same(ra, rb):
    if ra.ok and rb.ok: return norm_result(ra.result) == norm_result(rb.result)
    if not ra.ok and not rb.ok:
        # both fail: same failure class (timeout / crash text) counts as agreement
        return ra.timed_out == rb.timed_out and (ra.error[:40] == rb.error[:40])
    return False


def _split_tuple(tree, k):
    """(r1 (r2 (... rk))) -> [r1..rk] as parse trees, or None"""
    out = []
    for _ in range(k - 1):
        if not (isinstance(tree, tuple) and tree[0] == "con"): return None
        out.append(tree[1]); tree = tree[2]
    out.append(tree)
    return out


def _batch_net(case, book, vals, tag):
    t = case.inp if case.inp is not None else case.prog.inp
    calls, defs, rs = [], [], []
    for j, v in enumerate(vals):
        root, ds = encode(v, t, tag=f"{tag}{j}")
        calls.append(f"  & @prog ~ ({root} r{j})"); defs += ds; rs.append(f"r{j}")
    tup = rs[-1]
    for r in reversed(rs[:-1]): tup = f"({r} {tup})"
    return f"@main = {tup}\n" + "\n".join(calls) + "\n\n" + "\n".join(defs) + "\n\n" + book + "\n"


def run_batched(case, book, vals, timeout=120.0, tag="i"):
    """One executor process for many inputs. Returns a list of parse trees / None per input (None = failed), or None if the
    whole batch failed (caller falls back to one run per input)."""
    from genome.types import _parse_tree
    if len(vals) == 1:
        r = run_net(assemble_side(case, book, vals[0]), "run", timeout)
        return [_parse_tree(r.result)] if r.ok else None
    r = run_net(_batch_net(case, book, vals, tag), "run", timeout)
    if not r.ok: return None
    try: return _split_tuple(_parse_tree(r.result), len(vals))
    except Exception: return None


def sample_pair(case, n=200, seed=1000, workers=4, timeout=20.0, batch=40, first_only=False):
    vals = inputs_for(case, n, seed)
    res = {"n": len(vals), "agree": 0, "disagree": 0, "witnesses": [], "batched": 0, "fallback": 0}
    chunks = [vals[i:i + batch] for i in range(0, len(vals), batch)]

    def one_chunk(ch):
        ta = run_batched(case, case.A, ch, timeout=timeout * 6, tag="a")
        tb = run_batched(case, case.B, ch, timeout=timeout * 6, tag="b") if ta is not None else None
        if ta is not None and tb is not None:
            return [(v, x == y, str(x)[:200], str(y)[:200]) for v, x, y in zip(ch, ta, tb)], True
        out = []
        for v in ch:
            ra, rb = run_both(case, v, timeout)
            same = _same(ra, rb)
            out.append((v, same, (ra.result if ra.ok else "ERR " + ra.error)[:200], (rb.result if rb.ok else "ERR " + rb.error)[:200]))
            if first_only and not same: break
        return out, False

    with ThreadPoolExecutor(workers) as ex:
        for rows, was_batched in ex.map(one_chunk, chunks):
            res["batched" if was_batched else "fallback"] += len(rows)
            for v, same, a, b in rows:
                if same: res["agree"] += 1
                else:
                    res["disagree"] += 1
                    if len(res["witnesses"]) < 3: res["witnesses"].append({"input": repr(v)[:200], "A": a, "B": b})
    return res
