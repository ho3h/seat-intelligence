"""exp13: parametric verified list words. Each word is ONE hand-written HVM2 net template (Python function -> net text)
whose hole constants are literals. Every word defines `@prog = (l out)` so words compose with genome.compose.compose_nets.

A term is a tuple: (word, *params). Expressions (map holes) and predicates (filter holes) are tuples too:
  E: ("lin",a,b) x*a+b | ("xor",m) | ("and",m) | ("add",c) | ("sq",) | ("mod",m) | ("div",a) | ("ind",P) (P(x) as 0/1)
  P: ("gt",k) | ("lt",k) | ("ge",k) | ("even",) | ("odd",) | ("modeq",m,r)
Stages (list -> list): map E, filter P, take k, drop k, reverse, dedup (collapse runs), runsum, sort,
                        runmax, runmin, runxor, diff
Reducers (list -> u24): sum count max min xor first last cntgtfirst, idxfirst P, idxlast P, idxsum P, argmax
"""
from __future__ import annotations
from functools import reduce as _reduce

M = 1 << 24
BIG = M - 1


# ------------------------------------------------------------------ Python semantics
def pred_py(P):
    k = P[0]
    if k == "gt": return lambda x: x > P[1]
    if k == "lt": return lambda x: x < P[1]
    if k == "ge": return lambda x: x >= P[1]
    if k == "even": return lambda x: x % 2 == 0
    if k == "odd": return lambda x: x % 2 == 1
    if k == "modeq": return lambda x: x % P[1] == P[2]
    raise KeyError(P)


def expr_py(E):
    k = E[0]
    if k == "lin": return lambda x: (x * E[1] + E[2]) % M
    if k == "xor": return lambda x: x ^ E[1]
    if k == "and": return lambda x: x & E[1]
    if k == "add": return lambda x: (x + E[1]) % M
    if k == "sq": return lambda x: x * x % M
    if k == "mod": return lambda x: x % E[1]
    if k == "div": return lambda x: x // E[1]
    if k == "ind":
        p = pred_py(E[1]); return lambda x: 1 if p(x) else 0
    raise KeyError(E)


def _runop(xs, f):
    out = []
    for i, x in enumerate(xs): out.append(x if i == 0 else f(out[-1], x))
    return out


def stage_py(S):
    k = S[0]
    if k == "map": f = expr_py(S[1]); return lambda xs: [f(x) for x in xs]
    if k == "filter": p = pred_py(S[1]); return lambda xs: [x for x in xs if p(x)]
    if k == "take": return lambda xs: xs[:S[1]]
    if k == "drop": return lambda xs: xs[S[1]:]
    if k == "reverse": return lambda xs: xs[::-1]
    if k == "dedup": return lambda xs: [x for i, x in enumerate(xs) if i == 0 or xs[i - 1] != x]
    if k == "runsum": return lambda xs: _runop(xs, lambda a, b: (a + b) % M)
    if k == "sort": return lambda xs: sorted(xs)
    if k == "runmax": return lambda xs: _runop(xs, max)
    if k == "runmin": return lambda xs: _runop(xs, min)
    if k == "runxor": return lambda xs: _runop(xs, lambda a, b: a ^ b)
    if k == "diff": return lambda xs: [(xs[i + 1] - xs[i]) % M for i in range(len(xs) - 1)]
    raise KeyError(S)


def reducer_py(R):
    k = R[0]
    if k == "sum": return lambda xs: sum(xs) % M
    if k == "count": return len
    if k == "max": return lambda xs: max(xs, default=0)
    if k == "min": return lambda xs: min(xs, default=BIG)
    if k == "xor": return lambda xs: _reduce(lambda a, b: a ^ b, xs, 0)
    if k == "first": return lambda xs: xs[0] if xs else 0
    if k == "last": return lambda xs: xs[-1] if xs else 0
    if k == "cntgtfirst": return lambda xs: sum(1 for x in xs[1:] if x > xs[0]) if xs else 0
    if k == "idxfirst": p = pred_py(R[1]); return lambda xs: next((i for i, x in enumerate(xs) if p(x)), BIG)
    if k == "idxlast": p = pred_py(R[1]); return lambda xs: max((i for i, x in enumerate(xs) if p(x)), default=BIG)
    if k == "idxsum": p = pred_py(R[1]); return lambda xs: sum(i for i, x in enumerate(xs) if p(x)) % M
    if k == "argmax": return lambda xs: xs.index(max(xs)) if xs else 0
    raise KeyError(R)


def program_py(stages, reducer=None):
    fs = [stage_py(s) for s in stages]; rf = reducer_py(reducer) if reducer else None
    def run(xs):
        for f in fs: xs = f(xs)
        return rf(xs) if rf else xs
    return run


def show(t):
    if isinstance(t, tuple):
        if len(t) == 1: return t[0]
        return t[0] + "(" + ",".join(show(a) for a in t[1:]) + ")"
    return str(t)


# ------------------------------------------------------------------ net emitters for the holes
class Fresh:
    def __init__(self): self.n = 0
    def __call__(self, base="w"):
        self.n += 1; return f"{base}{self.n}"


def emit_pred(P, x, c, fr):
    """redexes computing boolean c (0/1) from number wire x."""
    k = P[0]
    if k == "gt": return [f"{x} ~ $([>] $({P[1]} {c}))"]
    if k == "lt": return [f"{x} ~ $([<] $({P[1]} {c}))"]
    if k == "ge": z = fr("z"); return [f"{x} ~ $([<] $({P[1]} {z}))", f"{z} ~ $([^] $(1 {c}))"]
    if k == "odd": return [f"{x} ~ $([&] $(1 {c}))"]
    if k == "even": z = fr("z"); return [f"{x} ~ $([&] $(1 {z}))", f"{z} ~ $([^] $(1 {c}))"]
    if k == "modeq": z = fr("z"); return [f"{x} ~ $([%] $({P[1]} {z}))", f"{z} ~ $([=] $({P[2]} {c}))"]
    raise KeyError(P)


def emit_expr(E, x, y, fr):
    """redexes computing number wire y = E(x)."""
    k = E[0]
    if k == "lin": z = fr("z"); return [f"{x} ~ $([*] $({E[1]} {z}))", f"{z} ~ $([+] $({E[2]} {y}))"]
    if k == "xor": return [f"{x} ~ $([^] $({E[1]} {y}))"]
    if k == "and": return [f"{x} ~ $([&] $({E[1]} {y}))"]
    if k == "add": return [f"{x} ~ $([+] $({E[1]} {y}))"]
    if k == "sq": a, b = fr("a"), fr("b"); return [f"{x} ~ {{{a} {b}}}", f"{a} ~ $([*] $({b} {y}))"]
    if k == "mod": return [f"{x} ~ $([%] $({E[1]} {y}))"]
    if k == "div": return [f"{x} ~ $([/] $({E[1]} {y}))"]
    if k == "ind": return emit_pred(E[1], x, y, fr)
    raise KeyError(E)


def _book(defs):
    """defs: list of (name, root, [redex strings])"""
    out = []
    for n, root, reds in defs:
        out.append(f"@{n} = {root}" + "".join(f"\n  & {r}" for r in reds))
    return "\n\n".join(out) + "\n"


def _walk(W, ctx):
    """match list wire l: returns the root pattern of a walker that takes the list first: ((?((W_nil W_cons) (p CTX)) p) CTX)"""
    return f"((?((@{W}_nil @{W}_cons) (p {ctx})) p) {ctx})"


# ------------------------------------------------------------------ stage templates
def net_stage(S):
    fr = Fresh(); k = S[0]
    if k == "map":
        return _book([("prog", "(l out)", ["@mp ~ (l out)"]),
                      ("mp", _walk("mp", "out"), []),
                      ("mp_nil", "(* (0 *))", []),
                      ("mp_cons", "(* ((h t) (1 (y t2))))", emit_expr(S[1], "h", "y", fr) + ["@mp ~ (t t2)"])])
    if k == "filter":
        return _book([("prog", "(l out)", ["@fl ~ (l out)"]),
                      ("fl", _walk("fl", "out"), []),
                      ("fl_nil", "(* (0 *))", []),
                      ("fl_cons", "(* ((h t) out))", ["h ~ {h1 h2}"] + emit_pred(S[1], "h1", "c", fr)
                       + ["c ~ ?((@fl_no @fl_yes) (h2 (t out)))"]),
                      ("fl_no", "(* (t out))", ["@fl ~ (t out)"]),
                      ("fl_yes", "(* (h (t (1 (h t2)))))", ["@fl ~ (t t2)"])])
    if k == "take":
        return _book([("prog", "(l out)", [f"@tk ~ (l ({S[1]} out))"]),
                      ("tk", "(l (k out))", ["k ~ ?((@tk_z @tk_s) (l out))"]),
                      ("tk_z", "(* (0 *))", []),
                      ("tk_s", "(k1 (l out))", ["l ~ (?((@tk_nil @tk_cons) (p (k1 out))) p)"]),
                      ("tk_nil", "(* (* (0 *)))", []),
                      ("tk_cons", "(* ((h t) (k1 (1 (h t2)))))", ["@tk ~ (t (k1 t2))"])])
    if k == "drop":
        return _book([("prog", "(l out)", [f"@dr ~ (l ({S[1]} out))"]),
                      ("dr", "(l (k out))", ["k ~ ?((@dr_z @dr_s) (l out))"]),
                      ("dr_z", "(l l)", []),
                      ("dr_s", "(k1 (l out))", ["l ~ (?((@dr_nil @dr_cons) (p (k1 out))) p)"]),
                      ("dr_nil", "(* (* (0 *)))", []),
                      ("dr_cons", "(* ((* t) (k1 out)))", ["@dr ~ (t (k1 out))"])])
    if k == "reverse":
        return _book([("prog", "(l out)", ["@rv ~ (l ((0 *) out))"]),
                      ("rv", _walk("rv", "(a out)"), []),
                      ("rv_nil", "(* (a a))", []),
                      ("rv_cons", "(* ((h t) (a out)))", ["@rv ~ (t ((1 (h a)) out))"])])
    if k == "dedup":
        return _book([("prog", "(l out)", ["@dd ~ (l out)"]),
                      ("dd", _walk("dd", "out"), []),
                      ("dd_nil", "(* (0 *))", []),
                      ("dd_cons", "(* ((h t) (1 (h1 t2))))", ["h ~ {h1 h2}", "@de ~ (t (h2 t2))"]),
                      ("de", _walk("de", "(v out)"), []),
                      ("de_nil", "(* (* (0 *)))", []),
                      ("de_cons", "(* ((h t) (v out)))", ["h ~ {h1 h2}", "h1 ~ $([=] $(v c))", "c ~ ?((@de_new @de_same) (h2 (t out)))"]),
                      ("de_new", "(h (t (1 (h1 t2))))", ["h ~ {h1 h2}", "@de ~ (t (h2 t2))"]),
                      ("de_same", "(* (h (t out)))", ["@de ~ (t (h out))"])])
    if k in ("runsum", "runxor"):
        op = "+" if k == "runsum" else "^"
        return _book([("prog", "(l out)", ["@rs ~ (l (0 out))"]),
                      ("rs", _walk("rs", "(a out)"), []),
                      ("rs_nil", "(* (* (0 *)))", []),
                      ("rs_cons", "(* ((h t) (a (1 (s1 t2)))))", [f"h ~ $([{op}] $(a s))", "s ~ {s1 s2}", "@rs ~ (t (s2 t2))"])])
    if k in ("runmax", "runmin"):
        cmp = ">" if k == "runmax" else "<"
        return _book([("prog", "(l out)", ["@rm ~ (l out)"]),
                      ("rm", _walk("rm", "out"), []),
                      ("rm_nil", "(* (0 *))", []),
                      ("rm_cons", "(* ((h t) (1 (h1 t2))))", ["h ~ {h1 h2}", "@rn ~ (t (h2 t2))"]),
                      ("rn", _walk("rn", "(a out)"), []),
                      ("rn_nil", "(* (* (0 *)))", []),
                      ("rn_cons", "(* ((h t) (a (1 (m1 t2)))))", ["h ~ {h1 h2}", "a ~ {a1 a2}", f"h1 ~ $([{cmp}] $(a1 c))",
                                                                  "c ~ ?((@rn_keep @rn_take) (h2 (a2 m)))", "m ~ {m1 m2}", "@rn ~ (t (m2 t2))"]),
                      ("rn_keep", "(* (a a))", []),
                      ("rn_take", "(* (h (* h)))", [])])
    if k == "diff":
        return _book([("prog", "(l out)", ["@df ~ (l out)"]),
                      ("df", _walk("df", "out"), []),
                      ("df_nil", "(* (0 *))", []),
                      ("df_cons", "(* ((h t) out))", ["@dg ~ (t (h out))"]),
                      ("dg", _walk("dg", "(v out)"), []),
                      ("dg_nil", "(* (* (0 *)))", []),
                      ("dg_cons", "(* ((h t) (v (1 (d t2)))))", ["h ~ {h1 h2}", "h1 ~ $([-] $(v d))", "@dg ~ (t (h2 t2))"])])
    if k == "sort":
        return _book([("prog", "(l out)", ["@so ~ (l ((0 *) out))"]),
                      ("so", _walk("so", "(a out)"), []),
                      ("so_nil", "(* (a a))", []),
                      ("so_cons", "(* ((h t) (a out)))", ["@ins ~ (h (a a2))", "@so ~ (t (a2 out))"]),
                      ("ins", "(x (l out))", ["l ~ (?((@ins_nil @ins_cons) (p (x out))) p)"]),
                      ("ins_nil", "(* (x (1 (x (0 *)))))", []),
                      ("ins_cons", "(* ((h t) (x out)))", ["x ~ {x1 x2}", "h ~ {h1 h2}", "x1 ~ $([>] $(h1 c))",
                                                          "c ~ ?((@ins_here @ins_later) (x2 (h2 (t out))))"]),
                      ("ins_here", "(x (h (t (1 (x (1 (h t)))))))", []),
                      ("ins_later", "(* (x (h (t (1 (h r))))))", ["@ins ~ (x (t r))"])])
    raise KeyError(S)


# ------------------------------------------------------------------ reducer templates
def _acc_reducer(init, cons_reds, nilv="a"):
    return [("prog", "(l out)", [f"@rd ~ (l ({init} out))"]),
            ("rd", _walk("rd", "(a out)"), []),
            ("rd_nil", f"(* (a a))" if nilv == "a" else f"(* ({nilv} *))", []),
            ("rd_cons", "(* ((h t) (a out)))", cons_reds + ["@rd ~ (t (a2 out))"])]


def net_reducer(R):
    fr = Fresh(); k = R[0]
    if k in ("sum", "xor"):
        return _book(_acc_reducer(0, [f"h ~ $([{'+' if k == 'sum' else '^'}] $(a a2))"]))
    if k == "count":
        return _book(_acc_reducer(0, ["h ~ *", "a ~ $([+] $(1 a2))"]))
    if k in ("max", "min"):
        cmp = ">" if k == "max" else "<"
        d = _acc_reducer(0 if k == "max" else BIG, ["h ~ {h1 h2}", "a ~ {a1 a2x}", f"h1 ~ $([{cmp}] $(a1 c))",
                                                    "c ~ ?((@rd_keep @rd_take) (h2 (a2x a2)))"])
        return _book(d + [("rd_keep", "(* (a a))", []), ("rd_take", "(* (h (* h)))", [])])
    if k == "last":
        return _book([("prog", "(l out)", ["@rd ~ (l (0 out))"]),
                      ("rd", _walk("rd", "(a out)"), []),
                      ("rd_nil", "(* (a a))", []),
                      ("rd_cons", "(* ((h t) (* out)))", ["@rd ~ (t (h out))"])])
    if k == "first":
        return _book([("prog", "(l out)", ["@rd ~ (l out)"]),
                      ("rd", _walk("rd", "out"), []),
                      ("rd_nil", "(* 0)", []),
                      ("rd_cons", "(* ((h *) h))", [])])
    if k == "cntgtfirst":
        return _book([("prog", "(l out)", ["@rd ~ (l out)"]),
                      ("rd", _walk("rd", "out"), []),
                      ("rd_nil", "(* 0)", []),
                      ("rd_cons", "(* ((h t) out))", ["@rg ~ (t (h (0 out)))"]),
                      ("rg", _walk("rg", "(f (a out))"), []),
                      ("rg_nil", "(* (* (a a)))", []),
                      ("rg_cons", "(* ((h t) (f (a out))))", ["f ~ {f1 f2}", "h ~ $([>] $(f1 c))", "c ~ $([+] $(a a2))",
                                                             "@rg ~ (t (f2 (a2 out)))"])])
    if k == "idxfirst":
        return _book([("prog", "(l out)", ["@rd ~ (l (0 out))"]),
                      ("rd", _walk("rd", "(i out)"), []),
                      ("rd_nil", f"(* (* {BIG}))", []),
                      ("rd_cons", "(* ((h t) (i out)))", emit_pred(R[1], "h", "c", fr) + ["c ~ ?((@rd_no @rd_yes) (t (i out)))"]),
                      ("rd_no", "(t (i out))", ["i ~ $([+] $(1 i2))", "@rd ~ (t (i2 out))"]),
                      ("rd_yes", "(* (* (i i)))", [])])
    if k in ("idxlast", "idxsum"):
        yes = ("(* (i1 (* i1)))", []) if k == "idxlast" else ("(* (i1 (a a2)))", ["a ~ $([+] $(i1 a2))"])
        init = BIG if k == "idxlast" else 0
        return _book([("prog", "(l out)", [f"@rd ~ (l (0 ({init} out)))"]),
                      ("rd", _walk("rd", "(i (a out))"), []),
                      ("rd_nil", "(* (* (a a)))", []),
                      ("rd_cons", "(* ((h t) (i (a out))))", ["i ~ {i1 i2}"] + emit_pred(R[1], "h", "c", fr)
                       + ["c ~ ?((@rd_no @rd_yes) (i1 (a a2)))", "i2 ~ $([+] $(1 i3))", "@rd ~ (t (i3 (a2 out)))"]),
                      ("rd_no", "(* (a a))", []),
                      ("rd_yes", *yes)])
    if k == "argmax":
        # state (best, bi, i): strict > keeps the first occurrence
        return _book([("prog", "(l out)", ["@rd ~ (l out)"]),
                      ("rd", _walk("rd", "out"), []),
                      ("rd_nil", "(* 0)", []),
                      ("rd_cons", "(* ((h t) out))", ["@ra ~ (t (h (0 (1 out))))"]),
                      ("ra", _walk("ra", "(b (j (i out)))"), []),
                      ("ra_nil", "(* (* (j (* j))))", []),
                      ("ra_cons", "(* ((h t) (b (j (i out)))))", ["h ~ {h1 h2}", "b ~ {b1 b2}", "i ~ {i1 i2}", "h1 ~ $([>] $(b1 c))",
                                                                   "c ~ ?((@ra_keep @ra_take) ((h2 (b2 nb)) (i1 (j nj))))",
                                                                   "i2 ~ $([+] $(1 i3))", "@ra ~ (t (nb (nj (i3 out))))"]),
                      ("ra_keep", "((* (b b)) (* (j j)))", []),
                      ("ra_take", "(* ((h (* h)) (i (* i))))", [])])
    raise KeyError(R)


def net_program(stages, reducer=None):
    """Lower a found program to one net by composing the template nets (genome.compose style, c{i}_ name prefixes)."""
    from genome.compose import compose_nets
    parts = [net_stage(s) for s in stages] + ([net_reducer(reducer)] if reducer else [])
    if not parts: parts = [_book([("prog", "(l l)", [])])]
    return parts[0] if len(parts) == 1 else compose_nets(parts)
