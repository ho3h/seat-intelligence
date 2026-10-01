"""netbuild: a tiny expression-DAG -> HVM2 text compiler, an AUTHORING AID for the HERO-3 benchmark (not part of the tester
or the rewriter, and never trusted: every net it emits is checked against a Python model and by the verifier).

Everything is branch-free arithmetic on 24-bit numbers, so a combiner is a dataflow of OPR nodes. Conditionals are
select(c, x, y) = c*x + (1-c)*y with c in {0,1}, which is exact modulo 2^24. A value used k times goes through a chain
of k-1 DUP nodes (numbers are freely copyable); a value never used is erased with `*`.

  build("comb", [2, 2], lambda a, b: (a[0] + b[0], a[1] + b[1]))
      -> "@comb = ((a0 a1) ((b0 b1) (o0 o1))) ..." : two 2-tuple arguments, one 2-tuple result.
An argument spec k means a right-nested k-tuple of numbers (k = 1: a bare number); a result of length k likewise.
"""
from __future__ import annotations

MASK = (1 << 24) - 1


class E:
    __slots__ = ("op", "a", "b", "val", "name", "uses", "id", "k")

    def __init__(self, op, a=None, b=None, val=None, name=None):
        self.op, self.a, self.b, self.val, self.name = op, a, b, val, name
        self.uses = 0; self.id = -1; self.k = 0

    # arithmetic (mod 2^24, matching the runtime)
    def __add__(s, o): return _bin("+", s, o)
    def __radd__(s, o): return _bin("+", o, s)
    def __sub__(s, o): return _bin("-", s, o)
    def __rsub__(s, o): return _bin("-", o, s)
    def __mul__(s, o): return _bin("*", s, o)
    def __rmul__(s, o): return _bin("*", o, s)
    def __and__(s, o): return _bin("&", s, o)
    def __rand__(s, o): return _bin("&", o, s)
    def __or__(s, o): return _bin("|", s, o)
    def __ror__(s, o): return _bin("|", o, s)
    def __xor__(s, o): return _bin("^", s, o)
    def __rxor__(s, o): return _bin("^", o, s)
    def __lshift__(s, o): return _bin("<<", s, o)
    def __rshift__(s, o): return _bin(">>", s, o)
    def __mod__(s, o): return _bin("%", s, o)
    def __floordiv__(s, o): return _bin("/", s, o)
    def __lt__(s, o): return _bin("<", s, o)
    def __gt__(s, o): return _bin(">", s, o)
    __hash__ = object.__hash__


def V(name): return E("var", name=name)


def C(v): return E("const", val=v & MASK)


def _lift(x): return x if isinstance(x, E) else C(int(x))


_PY = {"+": lambda a, b: (a + b) & MASK, "-": lambda a, b: (a - b) & MASK, "*": lambda a, b: (a * b) & MASK,
       "&": lambda a, b: a & b, "|": lambda a, b: a | b, "^": lambda a, b: a ^ b,
       "<<": lambda a, b: (a << b) & MASK, ">>": lambda a, b: a >> b,
       "<": lambda a, b: int(a < b), ">": lambda a, b: int(a > b), "=": lambda a, b: int(a == b), "!": lambda a, b: int(a != b)}


def _bin(op, a, b):
    a, b = _lift(a), _lift(b)
    if a.op == "const" and b.op == "const" and op in _PY:
        return C(_PY[op](a.val, b.val))
    return E(op, a, b)


def eq(a, b): return _bin("=", a, b)
def ne(a, b): return _bin("!", a, b)
def le(a, b): return _bin(">", a, b) ^ 1          # a <= b
def ge(a, b): return _bin("<", a, b) ^ 1          # a >= b
def lnot(c): return _lift(c) ^ 1                   # boolean not (c in {0,1})
def sel(c, x, y): return _lift(c) * _lift(x) + lnot(c) * _lift(y)
def mx(a, b): return sel(_bin(">", a, b), a, b)
def mn(a, b): return sel(_bin("<", a, b), a, b)


def _pat(names):
    if len(names) == 1: return names[0]
    return "(" + names[0] + " " + _pat(names[1:]) + ")"


def build(name: str, arg_arity: list[int], fn) -> str:
    """Compile fn(*args) -> E | tuple/list of E into `@name = (arg1 (arg2 ... result))`."""
    args, arg_names = [], []
    for i, k in enumerate(arg_arity):
        vs = [V(f"{'abcdefgh'[i]}{j}" if k > 1 else f"{'abcdefgh'[i]}") for j in range(k)]
        args.append(vs[0] if k == 1 else tuple(vs)); arg_names.append(vs)
    res = fn(*args)
    outs = list(res) if isinstance(res, (tuple, list)) else [res]
    outs = [_lift(o) for o in outs]
    # topological order + use counts
    order, seen = [], set()

    def visit(n):
        if n.op == "const": return
        n.uses += 1
        if id(n) in seen: return
        seen.add(id(n))
        if n.op != "var":
            visit(n.a); visit(n.b)
        order.append(n)

    for o in outs: visit(o)
    lines = []
    for i, n in enumerate(order): n.id = i
    for n in order: n.k = 0

    def wire_of(n):
        """Next consumer-side wire name of node n (or literal if const)."""
        if n.op == "const": return str(n.val)
        if n.uses == 1: return f"w{n.id}" if n.op != "var" else n.name
        w = f"{n.name if n.op == 'var' else 'w' + str(n.id)}_{n.k}"; n.k += 1
        return w

    for n in order:
        if n.op == "var": continue
        # consumer names for operands are handed out when the consumer is emitted
    body = []
    for n in order:
        if n.op == "var": continue
        x, y = wire_of(n.a), wire_of(n.b)
        r = f"w{n.id}" if n.uses <= 1 else f"w{n.id}"
        body.append(f"  & {x} ~ $([{n.op}] $({y} {r}))")
    # dup chains: node result wire w{id} (or var wire) feeds `uses` consumers named <src>_<k>
    dups = []
    for n in order:
        if n.uses >= 2:
            src = n.name if n.op == "var" else f"w{n.id}"
            names = [f"{src}_{k}" for k in range(n.uses)]
            cur = src
            for k in range(n.uses - 1):
                if k == n.uses - 2: dups.append(f"  & {cur} ~ {{{names[k]} {names[k+1]}}}")
                else:
                    nxt = f"{src}_t{k}"; dups.append(f"  & {cur} ~ {{{names[k]} {nxt}}}"); cur = nxt
    out_names = [wire_of(o) for o in outs]
    arg_pats = []
    for vs in arg_names:
        nm = [v.name if v.uses > 0 else "*" for v in vs]
        arg_pats.append(_pat(nm))
    # unused-variable objects were never visited: their uses is 0 -> `*`
    head = arg_pats[0]
    text = arg_pats[-1] if False else None
    pats = arg_pats + [_pat(out_names)]
    root = pats[-1]
    for p in reversed(pats[:-1]): root = f"({p} {root})"
    return f"@{name} = {root}\n" + "\n".join(dups + body) + ("\n" if dups or body else "")
