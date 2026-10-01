"""Executor-as-verifier. Every candidate net runs against a hidden suite; one failure means wrong.

Suite per program (seeded, deterministic): hand-picked edge cases, random inputs at authoring
sizes, and random inputs at the verifier-only sizes (up to 16x). The author gets back the
smallest failing input and the power metrics, never the suite itself.
"""
from __future__ import annotations
import hashlib, json, random, re, sys
from concurrent.futures import ThreadPoolExecutor
from .corpus import load_all, Program
from .types import encode, decode, DecodeError, describe
from .executor import run_net

N_SMALL, N_BIG, N_ENUM = 24, 6, 60
ENUM_VALS, ENUM_LEN = (0, 1, 2), 3
SUITE = "v2"  # v1 = edge + random; v2 adds the exhaustive small-input sweep


def enum_inputs(t):
    """All values of type t built from ENUM_VALS with lists up to ENUM_LEN long."""
    import itertools
    from .types import U24, List, Tup, Adt, Rec
    if isinstance(t, U24): return list(ENUM_VALS)
    if isinstance(t, Adt):
        def build(depth):
            if depth == 0: return [(i,) for i, c in enumerate(t.ctors) if not c]
            prev = build(depth - 1) or []
            out = list(prev)
            for i, c in enumerate(t.ctors):
                if not c: continue
                pools = [prev if isinstance(f, Rec) else enum_inputs(f) for f in c]
                pools = [p_[:4] for p_ in pools]
                for combo in itertools.product(*pools): out.append((i, *combo))
            return out
        vals = build(2)
        return vals if len(vals) <= 400 else vals[::max(1, len(vals) // 400)]
    if isinstance(t, List):
        el = enum_inputs(t.elem)
        el = el[:3] if len(el) > 3 else el
        return [list(c) for n in range(ENUM_LEN + 1) for c in itertools.product(el, repeat=n)]
    if isinstance(t, Tup):
        return [tuple(c) for c in itertools.product(*[enum_inputs(e) for e in t.elems])]
    raise TypeError(t)


def _rng(prog_id: str, seed: int) -> random.Random:
    h = hashlib.sha256(f"{prog_id}|{seed}".encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


def build_cases(p: Program, seed: int):
    rng = _rng(p.id, seed)
    cases = [("edge", None, e) for e in p.edges]
    cases += [("small", n, p.gen(rng, n)) for n in (rng.choice(p.sizes) for _ in range(N_SMALL))]
    cases += [("big", n, p.gen(rng, n)) for n in (p.test_sizes[i % len(p.test_sizes)] for i in range(N_BIG))]
    from .corpus.check import PRE
    pre = p.pre or PRE.get(p.id) or (lambda x: True)
    pool = [x for x in enum_inputs(p.inp) if pre(x)]
    if len(pool) > N_ENUM: pool = rng.sample(pool, N_ENUM)
    cases += [("enum", None, x) for x in pool]
    return cases


def assemble(p: Program, author_book: str, value) -> str:
    root, defs = encode(value, p.inp)
    return f"@main = r\n  & @prog ~ ({root} r)\n\n" + "\n".join(defs) + "\n\n" + author_book + "\n"


_DIG = {}


def _digest_for(p):
    from .digest import gen_digest
    if p.id not in _DIG: _DIG[p.id] = gen_digest(p.out)
    return _DIG[p.id]


def assemble_digest(p: Program, author_book: str, value) -> str:
    """Large cases: the author's output is folded to two hashes by the fixed digest net inside the executor."""
    book, root = _digest_for(p)
    root_in, defs = encode(value, p.inp)
    return (f"@main = r\n  & @prog ~ ({root_in} o)\n  & @{root} ~ (o ((0 0) r))\n\n" + "\n".join(defs)
            + "\n\n" + author_book + "\n\n" + book)


def digest_overhead(p: Program, expected) -> int:
    """Interactions the digest itself costs on this output (measured on the reference output alone)."""
    book, root = _digest_for(p)
    root_in, defs = encode(expected, p.out, tag="ex")
    r = run_net(f"@main = r\n  & @{root} ~ ({root_in} ((0 0) r))\n\n" + "\n".join(defs) + "\n\n" + book, "run", 120)
    return r.itrs if r.ok else 0


def lint_net(book: str) -> str | None:
    """Static diagnostics on the author's own net (the native arm's counterpart of a compiler's errors). Reads nothing from the
    hidden suite. Localised: names the definition and quotes the offending statement."""
    from .netast import tokens
    text = re.sub(r"//[^\n]*", "", book)
    text = re.sub(r"\[[^\]\s]*\]\d*", "0", text)  # operator literals like [&] must not look like redex markers
    # split into definitions at `@name =` at line start, and definitions into statements at `&`
    parts = re.split(r"(?m)^\s*(?=@[\w/]+\s*=)", text)
    msgs, defined, used = [], set(), set()
    for blk in parts:
        blk = blk.strip()
        if not blk: continue
        m = re.match(r"@([\w/]+)\s*=", blk)
        if not m: msgs.append("text outside any definition: `" + blk[:60].replace("\n", " ") + "`"); continue
        name = m.group(1); defined.add(name)
        body = blk[m.end():]
        stmts = [x.strip() for x in re.split(r"&!?", body)]
        cnt = {}
        for i, st in enumerate(stmts):
            label = "the root tree" if i == 0 else f"the redex `& {st[:70]}`"
            depth = 0
            for ch in st:
                depth += ch in "({"; depth -= ch in ")}"
                if depth < 0: break
            if depth != 0:
                msgs.append(f"@{name}: brackets do not balance in {label if i == 0 else label + ('...' if len(st) > 70 else '')} "
                            f"({'a closing bracket has no opener' if depth < 0 else str(depth) + ' opener(s) never closed'})")
            if i > 0 and st.count("~") != 1: msgs.append(f"@{name}: a redex must have exactly one `~`: `& {st[:70]}`")
            for tk in tokens(st):
                if tk.startswith("@"): used.add(tk[1:])
                elif re.fullmatch(r"[A-Za-z_]\w*", tk): cnt[tk] = cnt.get(tk, 0) + 1
        for v, c in sorted(cnt.items()):
            where = [("root" if i == 0 else "& " + st[:40]) for i, st in enumerate(stmts) if re.search(rf"(?<![\w@]){re.escape(v)}(?![\w])", st)] or ["the definition"]
            if c == 1: msgs.append(f"@{name}: wire `{v}` appears only once (in {where[0]}); a wire needs exactly two ends. Erase an unused value with `*`.")
            elif c > 2: msgs.append(f"@{name}: wire `{v}` appears {c} times; a wire has exactly two ends. Duplicate a value with a {{ }} node.")
    for r in sorted(used - defined):
        if not r.startswith("__"): msgs.append(f"reference @{r} is not defined")
    return "\n".join(msgs[:8]) if msgs else None


def check_book(author_book: str) -> str | None:
    if re.search(r"^\s*@main\s*=", author_book, re.M): return "do not define @main; the harness owns it"
    if not re.search(r"^\s*@prog\s*=", author_book, re.M): return "no @prog definition found"
    if re.search(r"@__", author_book): return "names starting with __ are reserved for the harness"
    lint = lint_net(author_book)
    if lint: return "static check failed before running:\n" + lint
    return None


def _short(x, n=240):
    s = repr(x)
    return s if len(s) <= n else s[:n] + f"… (len {len(x) if hasattr(x, '__len__') else '?'})"


def verify(p: Program, author_book: str, seed: int = 0, timeout: float = 30.0, workers: int = 16) -> dict:
    bad = check_book(author_book)
    if bad: return {"status": "reject", "reason": bad}
    cases = build_cases(p, seed)

    def one(c):
        kind, n, x = c
        exp = p.ref(x)
        use_digest = kind == "big"
        r = run_net(assemble_digest(p, author_book, x) if use_digest else assemble(p, author_book, x), "run", timeout)
        rec = {"kind": kind, "size": n, "itrs": r.itrs, "secs": r.secs, "input": x, "expected": exp}
        if not r.ok:
            rec.update(ok=False, why="net did not run to a result", got=r.error); return rec
        if use_digest:
            from .digest import py_digest
            from .types import tup, u24
            try:
                got_d = decode(r.result, tup(u24, u24))
            except DecodeError as e:
                rec.update(ok=False, why=f"output not fully evaluated / not canonical (digest could not fold it): {e}",
                           got=r.result[:240]); return rec
            want_d = py_digest(exp, p.out)
            rec["got"] = f"<digest {got_d}>"; rec["expected"] = f"<digest {want_d}> (output of {len(repr(exp))} chars)"
            rec["ok"] = got_d == want_d
            if not rec["ok"]: rec["why"] = "wrong answer (large case, compared by digest of the full output)"
            else:
                # power on the bare program: interactions and parallel depth, no digest in the way
                m = run_net(assemble(p, author_book, x), "depth", timeout * 4)
                if m.ok: rec["itrs"], rec["depth"] = m.itrs, m.depth
            return rec
        try:
            got = decode(r.result, p.out)
        except DecodeError as e:
            rec.update(ok=False, why=f"result is not the canonical encoding: {e}", got=r.result[:240]); return rec
        rec["got"] = got
        rec["ok"] = got == exp
        if not rec["ok"]: rec["why"] = "wrong answer"
        return rec

    with ThreadPoolExecutor(workers) as ex:
        recs = list(ex.map(one, cases))
    fails = [r for r in recs if not r["ok"]]
    out = {"status": "pass" if not fails else "fail", "cases": len(recs), "failed": len(fails),
           "seed": seed, "suite": SUITE, "metrics": _metrics(recs)}
    if fails:
        f = min(fails, key=lambda r: len(repr(r["input"])))
        out["counterexample"] = {"why": f["why"], "kind": f["kind"], "size": f["size"],
                                 "input": _short(f["input"]), "expected": _short(f["expected"]), "got": _short(f["got"])}
    return out


def _metrics(recs):
    ok = [r for r in recs if r["ok"]]
    big = [r["itrs"] for r in ok if r["kind"] == "big"]
    small = [r["itrs"] for r in ok if r["kind"] == "small"]
    med = lambda v: sorted(v)[len(v) // 2] if v else None
    dep = [r["depth"] for r in ok if r.get("depth")]
    return {"itrs_median_small": med(small), "itrs_median_big": med(big), "itrs_max": max((r["itrs"] for r in ok), default=None),
            "depth_median_big": med(dep), "depth_max": max(dep, default=None)}


def feedback_text(p: Program, res: dict) -> str:
    if res["status"] == "pass":
        m = res["metrics"]
        return f"PASS on all {res['cases']} hidden cases. Interactions: median {m['itrs_median_small']} at authoring sizes, median {m['itrs_median_big']} at the largest sizes."
    if res["status"] == "reject":
        return f"REJECTED before running: {res['reason']}"
    c = res["counterexample"]
    return (f"FAIL: {res['failed']} of {res['cases']} hidden cases wrong. Smallest failing case ({c['kind']}, size {c['size']}):\n"
            f"  reason:   {c['why']}\n  input:    {c['input']}\n  expected: {c['expected']}\n  got:      {c['got']}")


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("prog"); ap.add_argument("net"); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--json", action="store_true"); ap.add_argument("--timeout", type=float, default=30.0)
    a = ap.parse_args(argv)
    p = load_all()[a.prog]
    res = verify(p, open(a.net).read(), a.seed, a.timeout)
    print(json.dumps(res, default=str) if a.json else feedback_text(p, res))
    return 0 if res["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


# ------------------------------------------------------------------ B1: the same author, the human route (Bend)
def verify_b1(p: Program, bend_code: str, seed: int = 0, timeout: float = 30.0, workers: int = 16, hvm_book: str | None = None) -> dict:
    """Bend author code must define `def prog(x)`. Same suite, same executor, same metrics as the native arm."""
    from . import bend_io as B
    from .digest import py_digest
    from .types import tup, u24
    if hvm_book is None:
        if not re.search(r"^def\s+prog\s*\(", bend_code, re.M): return {"status": "reject", "reason": "no `def prog(x)` found"}
        if re.search(r"^def\s+main\s*\(", bend_code, re.M): return {"status": "reject", "reason": "do not define main; the harness owns it"}
        book, err = B.compile_bend(B.bend_source(p, bend_code))
        if err: return {"status": "reject", "reason": "Bend did not compile:\n" + err}
    else:
        book = hvm_book
    dbook, droot = B.gen_digest_bend(p.out)
    cases = build_cases(p, seed)

    def one(c):
        kind, n, x = c
        exp = p.ref(x); rec = {"kind": kind, "size": n, "input": x, "expected": exp, "itrs": 0, "secs": 0}
        small = kind != "big"
        if small:
            r = run_net(B.assemble_bend(p, book, x, digest=False), "run", timeout)
            if not r.ok: rec.update(ok=False, why="net did not run to a result", got=r.error); return rec
            try: got = B.decode_bend(r.result, p.out)
            except Exception as e: rec.update(ok=False, why=f"result is not a well-formed value: {e}", got=r.result[:240]); return rec
            rec["got"] = got; rec["ok"] = got == exp
            if not rec["ok"]: rec["why"] = "wrong answer"; return rec
            rec["itrs"] = r.itrs; return rec
        r = run_net(B.assemble_bend(p, book, x, digest=True), "run", timeout)
        if not r.ok: rec.update(ok=False, why="net did not run to a result", got=r.error); return rec
        try: got_d = decode(r.result, tup(u24, u24))
        except DecodeError as e: rec.update(ok=False, why=f"output not fully evaluated / not a value: {e}", got=r.result[:240]); return rec
        want_d = py_digest(exp, p.out)
        rec["ok"] = got_d == want_d; rec["got"] = f"<digest {got_d}>"; rec["expected"] = f"<digest {want_d}> (output of {len(repr(exp))} chars)"
        if not rec["ok"]: rec["why"] = "wrong answer (large case, compared by digest of the full output)"; return rec
        m = run_net(B.assemble_bend(p, book, x, digest=False), "depth", timeout * 4)
        if m.ok: rec["itrs"], rec["depth"] = m.itrs, m.depth
        return rec

    with ThreadPoolExecutor(workers) as ex: recs = list(ex.map(one, cases))
    fails = [r for r in recs if not r["ok"]]
    out = {"status": "pass" if not fails else "fail", "cases": len(recs), "failed": len(fails), "seed": seed, "suite": SUITE, "arm": "B1",
           "metrics": _metrics(recs)}
    if fails:
        f = min(fails, key=lambda r: len(repr(r["input"])))
        out["counterexample"] = {"why": f["why"], "kind": f["kind"], "size": f["size"], "input": _short(f["input"]),
                                 "expected": _short(f["expected"]), "got": _short(f["got"])}
    return out
