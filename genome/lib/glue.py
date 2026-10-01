"""glue: typed, checked composition over graphprims (swing 23, 2026-09-30).

graphprims removes the wiring INSIDE primitives; this layer removes the wiring BETWEEN them. The author never writes
HVM text. Every definition (the `@prog` root, a walker step, a leaf body, a branch) is a Python function that receives
wires as arguments, calls primitives and operators on them, and returns wires. Every primitive has a declared port
signature (name, direction, kind, how many connections), and the checker raises a readable GlueError, naming the
author's source line, BEFORE anything runs:

  * unconnected input port / unknown port name          (call time)
  * value used twice (port connected twice)             (at the second use, with the first use's location)
  * kind mismatch (e.g. a list where a trie is expected) (call time)
  * a value that is needed k times without a duplicator  -> d.fanout(w, k) inserts the DUP chain
  * an output / argument never used                      -> d.erase(w), or d.erase_unused() (auto-erase helper)
  * wrong arity: a body function taking or returning the wrong number of values
  * a wire captured from another definition (Python closure over another body's wire)
  * duplicating a trie / list / request trie (unsafe with unlabelled DUPs)
  * name clashes between primitive instances

The emitted net is the same net a careful hand author would write (graphprims emits the primitives; glue only emits the
author's bodies), so composition through this layer costs nothing measurable (see test_glue.py, docs/TYPED-GLUE.md).

Quick example (t3_degrees):

    from genome.lib.glue import Program, NUM, DEPTH, EDGE
    P = Program()
    lg = P.lg(); z0 = P.const_trie("z0", 0); inc = P.update("dinc", "inc"); tl = P.to_list("tl")
    def step(d, L, h, u, v):                        # state (L, h), element (u, v)
        L1, L2, L3 = d.fanout(L, 3)
        h1 = d.call(inc, t=h, k=u, L=L1)
        return L3, d.call(inc, t=h1, k=v, L=L2)
    def fin(d, L, h):
        d.erase(L); return h
    w = P.stream("w", step, fin, state=[("L", DEPTH), ("h", TRIE(NUM))], elem=EDGE)
    def prog(d, n, es):
        def empty(b, es): b.erase(es); return b.nil()
        def nonempty(b, nm1, es):
            L = b.call(lg, x=nm1); L1, L2, L3 = b.fanout(L, 3)
            H = b.call(w, list=es, init=(L2, b.call(z0, L=L1)))
            n = b.op(nm1, "+", 1)
            return b.call(tl, t=H, L=L3, n=n)
        return d.branch(n, empty, nonempty, es)
    P.prog("t3_degrees", prog)
    P.write("t3_degrees.hvm")
"""
from __future__ import annotations
import inspect, os, re
from . import graphprims as G
from .graphprims import Book, INF

__all__ = ["Program", "GlueError", "Kind", "NUM", "DEPTH", "ANY", "MCQ", "LIST", "TRIE", "TUP", "HOLE", "EDGE",
           "EDGES", "WEDGE", "WEDGES", "ADJ", "INF", "Lit"]


class GlueError(Exception):
    """A composition mistake, found before the net runs. The message names the author's source line."""

    def __init__(self, msg):
        super().__init__(msg)
        try:  # exp14/exp20 bookkeeping: log checker catches next to the author's build script
            for fr in inspect.stack()[1:]:
                f = os.path.abspath(fr.filename)
                if f != _HERE and (os.sep + "exp14" + os.sep in f or os.sep + "exp20" + os.sep in f) and f.endswith("build.py"):
                    import time
                    with open(os.path.join(os.path.dirname(f), "glue_errors.log"), "a") as lf:
                        lf.write(f"--- {time.strftime('%H:%M:%S')}\n{msg}\n")
                    break
        except Exception:
            pass


_HERE = os.path.abspath(__file__)


def _loc() -> str:
    """The author's source location (first stack frame outside this file)."""
    for fr in inspect.stack()[1:]:
        if os.path.abspath(fr.filename) != _HERE:
            return f"{os.path.basename(fr.filename)}:{fr.lineno}"
    return "?"


# ============================================================================ kinds
class Kind:
    """num | depth | any | mcq | list[k] | trie[k] | (k1 k2 ...) | hole[k] | 'a (type variable, per call)."""
    __slots__ = ("tag", "args")

    def __init__(self, tag, *args):
        self.tag, self.args = tag, args

    def __eq__(self, o): return isinstance(o, Kind) and self.tag == o.tag and self.args == o.args
    def __hash__(self): return hash((self.tag, self.args))

    def __str__(self):
        t, a = self.tag, self.args
        if t in ("num", "depth", "any"): return t
        if t == "mcq": return "request-trie"
        if t == "var": return "?"
        if self == ADJ: return "adj (trie[list[(num num)]])"
        if t == "list": return f"list[{a[0]}]"
        if t == "trie": return f"trie[{a[0]}]"
        if t == "hole": return f"hole[{a[0]}]"
        if t == "tup": return "(" + " ".join(map(str, a)) + ")"
        return t
    __repr__ = __str__


NUM, DEPTH, ANY, MCQ = Kind("num"), Kind("depth"), Kind("any"), Kind("mcq")
def LIST(e=ANY): return Kind("list", e)
def TRIE(e=NUM): return Kind("trie", e)
def TUP(*es): return Kind("tup", *es)
def HOLE(k): return Kind("hole", k)
def _V(n): return Kind("var", n)


EDGE = TUP(NUM, NUM)                 # (u v)
EDGES = LIST(EDGE)
WEDGE = TUP(NUM, NUM, NUM)           # (u (v w))
WEDGES = LIST(WEDGE)
ADJ = TRIE(LIST(TUP(NUM, NUM)))      # adjacency trie: leaf u = list of (v w)


def _subst(k, env):
    if k.tag == "var": return _subst(env[k.args[0]], env) if k.args[0] in env else k
    if k.args and isinstance(k.args[0], Kind): return Kind(k.tag, *[_subst(a, env) for a in k.args])
    return k


def _unify(port, got, env) -> bool:
    port = _subst(port, env)
    if port.tag == "var": env[port.args[0]] = got; return True
    if port.tag == "any" or got.tag in ("any", "var"): return True
    if port.tag == "num": return got.tag in ("num", "depth")
    if port.tag == "depth": return got.tag == "depth"
    if port.tag != got.tag or len(port.args) != len(got.args): return False
    return all(_unify(a, b, env) for a, b in zip(port.args, got.args))


def _copyable(k) -> bool:
    if k.tag in ("num", "depth", "any", "var"): return True
    if k.tag == "tup": return all(_copyable(a) for a in k.args)
    return False


def from_type(t) -> Kind:
    """Kind of a genome.types interface type."""
    from ..types import U24, List, Tup
    if isinstance(t, U24): return NUM
    if isinstance(t, List): return LIST(from_type(t.elem))
    if isinstance(t, Tup): return TUP(*[from_type(e) for e in t.elems])
    return ANY


# ============================================================================ values
class Lit:
    """A closed constant term (e.g. `(0 *)`), with its kind."""
    def __init__(self, text, kind): self.text, self.kind = text, kind
    def __repr__(self): return self.text


class Wire:
    """One end-to-end connection inside one definition. Use each wire exactly once."""
    def __init__(self, body, kind, hint, origin, slot=True, cell=None):
        self.body, self.kind, self.hint, self.origin, self.slot = body, kind, hint, origin, slot
        self.loc = _loc()
        self.uses: list[tuple[str, str]] = []
        self.erased = False
        self.cell = cell if cell is not None else [None]   # shared HVM name (hole pairs share one)

    def __repr__(self): return f"<wire {self.hint}: {self.kind} in @{self.body.name}>"

    def _desc(self): return f"`{self.hint}` ({self.kind}, {self.origin}, made at {self.loc})"

    # forbid accidental Python arithmetic on wires: a very common weak-author slip
    def _nope(self, *a):
        raise GlueError(f"{_loc()}: wires are not Python numbers; use d.op({self.hint}, '<op>', other) "
                        f"for arithmetic on `{self.hint}` ({self.kind}).")
    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = __lt__ = __gt__ = __le__ = __ge__ = _nope
    __and__ = __or__ = __xor__ = __rshift__ = __lshift__ = __floordiv__ = __truediv__ = __mod__ = _nope

    def __bool__(self):
        raise GlueError(f"{_loc()}: a wire has no Python truth value (its number is only known when the net runs); "
                        f"use d.select(c, a, b) or d.branch(c, ...) to decide on `{self.hint}`.")

    def __iter__(self):
        raise GlueError(f"{_loc()}: cannot unpack wire `{self.hint}` ({self.kind}) with Python; use d.split(w) "
                        f"for a tuple wire, or check the primitive's outputs with prim.help().")


def _kind_of(v) -> Kind:
    if isinstance(v, Wire): return v.kind
    if isinstance(v, bool): raise GlueError(f"{_loc()}: use 0/1, not a Python bool")
    if isinstance(v, int): return NUM
    if isinstance(v, Lit): return v.kind
    if isinstance(v, (tuple, list)): return TUP(*[_kind_of(x) for x in v])
    if v is None: raise GlueError(f"{_loc()}: got None where a value was expected (did a body function forget "
                                  f"`return`, or does the primitive have no output?)")
    raise GlueError(f"{_loc()}: {v!r} is not a glue value (a wire, an int, a Lit, or a tuple of these)")


# ============================================================================ ports and primitives
class Port:
    def __init__(self, name, d, kind, default=None, fields=None, doc=""):
        self.name, self.dir, self.kind, self.default, self.fields, self.doc = name, d, kind, default, fields, doc

    def __str__(self):
        k = self.kind
        if self.fields: k = "(" + " ".join(f"{n}:{fk}" for n, fk in self.fields) + ")"
        cnt = "exactly once" if self.dir == "out" or self.default is None else f"0..1, default {self.default!r}"
        return f"{self.dir:3s} {self.name}: {k}  [{cnt}]" + (f"  -- {self.doc}" if self.doc else "")


def _in(n, k, **kw): return Port(n, "in", k, **kw)
def _out(n, k, **kw): return Port(n, "out", k, **kw)


def chain(*xs):
    """Right-nested constructor tree (a (b (c d)))."""
    t = xs[-1]
    for x in reversed(xs[:-1]): t = (x, t)
    return t


def _ports(sig):
    if isinstance(sig, Port): return [sig]
    if isinstance(sig, tuple): return _ports(sig[0]) + _ports(sig[1])
    return []


class Prim:
    """A primitive instance: its entry definition, its port signature, and metadata used by other primitives."""
    def __init__(self, entry, desc, sig, **meta):
        self.entry, self.desc, self.sig, self.meta = entry, desc, sig, meta
        self.ports = _ports(sig)
        self.inputs = [p for p in self.ports if p.dir == "in"]
        self.outputs = [p for p in self.ports if p.dir == "out"]

    def signature(self) -> str:
        outs = ", ".join(p.name for p in self.outputs) or "nothing"
        return (f"{self.desc} (@{self.entry}); d.call returns {outs}:\n" +
                "\n".join("    " + str(p) for p in self.ports))

    def help(self): print(self.signature())
    def __repr__(self): return f"<prim {self.desc}>"


# ============================================================================ bodies
_OPS = {"+", "-", "*", "/", "%", "=", "!", "<", ">", "&", "|", "^", "<<", ">>"}


class Body:
    """The composer for ONE definition. Every method checks linearity and kinds as it goes."""

    def __init__(self, P, name, what):
        self.P, self.name, self.what = P, name, what
        self.stmts: list[list] = []
        self.wires: list[Wire] = []
        self.closed = False

    # ---------------------------------------------------------------- internals
    def _new(self, kind, hint, origin, slot=True, cell=None):
        w = Wire(self, kind, hint, origin, slot, cell)
        self.wires.append(w)
        return w

    def _use(self, v, desc):
        """Consume every wire inside value v exactly once."""
        if isinstance(v, Wire):
            if self.closed:
                raise GlueError(f"{_loc()}: {self.what} (@{self.name}) is already finished; wire {v._desc()} "
                                f"cannot be used after its body function returned.")
            if v.body is not self:
                raise GlueError(
                    f"{_loc()}: wire {v._desc()} belongs to {v.body.what} (@{v.body.name}), but is used in "
                    f"{self.what} (@{self.name}) ({desc}). Each definition has its own wires (no Python closures "
                    f"over wires): pass the value in through the state / environment / branch arguments.")
            if v.uses:
                u0 = v.uses[0]
                cnt = "It is needed at least twice: write  a, b = d.fanout(%s, 2)  and use each once." % v.hint
                if not _copyable(v.kind):
                    cnt = (f"A {v.kind} cannot be duplicated safely (HVM2 DUPs are unlabelled): restructure so it "
                           f"is used once, or get a second copy from a primitive (mc_deliver_keep returns a copy of "
                           f"a numeric trie; mapreduce rebuilds the trie it reduces).")
                raise GlueError(f"{_loc()}: wire {v._desc()} is used a second time ({desc}); it was already used "
                                f"at {u0[1]} ({u0[0]}). A wire has exactly two ends. {cnt}")
            v.uses.append((desc, _loc()))
            return
        if isinstance(v, (tuple, list)):
            for x in v: self._use(x, desc)
            return
        _kind_of(v)

    def _frag(self, v):
        """Fragments that print value v (after _use)."""
        if isinstance(v, Wire): return [("U", v)]
        if isinstance(v, int): return [str(v & 0xFFFFFF)]
        if isinstance(v, Lit): return [v.text]
        if isinstance(v, (tuple, list)):
            v = list(v)
            if len(v) == 1: return self._frag(v[0])
            return ["("] + self._frag(v[0]) + [" "] + self._frag(v[1:]) + [")"]
        raise GlueError(f"{_loc()}: cannot render {v!r}")

    def _check(self, want: Kind, v, env, where, fields=None):
        if isinstance(v, int) and not isinstance(v, bool) and _subst(want, env).tag in ("depth", "num", "any", "var"):
            return
        if fields and isinstance(v, (tuple, list)):
            if len(v) != len(fields):
                raise GlueError(f"{_loc()}: {where} takes {len(fields)} fields "
                                f"({' '.join(f'{n}:{k}' for n, k in fields)}); got a tuple of {len(v)}.")
            for (fn_, fk), x in zip(fields, v):
                self._check(fk, x, env, f"{where} field `{fn_}`")
            return
        got = _kind_of(v)
        if not _unify(want, got, env):
            src = f" `{v.hint}` from {v.origin} (made at {v.loc})" if isinstance(v, Wire) else f" {v!r}"
            hint = ""
            if _subst(want, env).tag == "depth" and got.tag == "num":
                hint = " Depths come from lg(); if this number really is a trie depth, use d.as_depth(x)."
            raise GlueError(f"{_loc()}: kind mismatch at {where}: expected {_subst(want, env)}, got {got}{src}.{hint}")

    # ---------------------------------------------------------------- author API
    def call(self, prim: Prim, **ports):
        """Connect a primitive. Keyword = port name. Returns its output wire (or a tuple in signature order, or
        None when it has no outputs)."""
        if not isinstance(prim, Prim):
            raise GlueError(f"{_loc()}: d.call needs a primitive made by the Program (e.g. P.update(...)); got {prim!r}")
        names = {p.name for p in prim.inputs}
        for k in ports:
            if k not in names:
                outs = {p.name for p in prim.outputs}
                why = "is an OUTPUT (it is returned by d.call, not passed in)" if k in outs else "does not exist"
                raise GlueError(f"{_loc()}: port `{k}` {why} on {prim.signature()}")
        vals = {}
        for p in prim.inputs:
            if p.name in ports: vals[p.name] = ports[p.name]
            elif p.default is not None: vals[p.name] = p.default
            else:
                raise GlueError(f"{_loc()}: input port `{p.name}` is not connected in this call of {prim.signature()}")
        env: dict = {}
        for p in prim.inputs:
            self._check(p.kind, vals[p.name], env, f"{prim.desc} port `{p.name}`", p.fields)
        for p in prim.inputs:
            self._use(vals[p.name], f"{prim.desc} port `{p.name}`")
        outs = []

        def walk(node):
            if isinstance(node, Port):
                if node.dir == "in": return self._frag(vals[node.name])
                if node.fields:
                    ws = [self._new(_subst(k, env), n, f"output `{node.name}.{n}` of {prim.desc}") for n, k in node.fields]
                    outs.extend(ws)
                    return self._pfrag(ws)
                w = self._new(_subst(node.kind, env), node.name, f"output `{node.name}` of {prim.desc}")
                outs.append(w)
                return [("P", w)]
            if isinstance(node, tuple):
                return ["("] + walk(node[0]) + [" "] + walk(node[1]) + [")"]
            return [str(node)]
        self.stmts.append([f"@{prim.entry} ~ "] + walk(prim.sig))
        if not outs: return None
        return outs[0] if len(outs) == 1 else tuple(outs)

    def _pfrag(self, ws):
        if len(ws) == 1: return [("P", ws[0])]
        return ["(", ("P", ws[0]), " "] + self._pfrag(ws[1:]) + [")"]

    def op(self, a, op: str, b):
        """Arithmetic / comparison on numbers: a op b (24-bit). op in + - * / % = ! < > & | ^ << >>.
        Comparisons return 1 or 0."""
        if op not in _OPS: raise GlueError(f"{_loc()}: unknown operator {op!r}; use one of {' '.join(sorted(_OPS))}")
        for x, s in ((a, "left"), (b, "right")):
            k = _kind_of(x)
            if k.tag not in ("num", "depth", "any"):
                raise GlueError(f"{_loc()}: operator `{op}` needs numbers; its {s} operand is {k}"
                                + (f" (`{x.hint}` from {x.origin})" if isinstance(x, Wire) else ""))
        if op in "/%" and isinstance(b, int) and b == 0: raise GlueError(f"{_loc()}: division by the constant 0")
        if isinstance(a, int) and isinstance(b, int):
            import operator as O
            f = {"+": O.add, "-": O.sub, "*": O.mul, "/": O.floordiv, "%": O.mod, "=": lambda x, y: int(x == y),
                 "!": lambda x, y: int(x != y), "<": lambda x, y: int(x < y), ">": lambda x, y: int(x > y),
                 "&": O.and_, "|": O.or_, "^": O.xor, "<<": O.lshift, ">>": O.rshift}[op]
            return f(a, b) & 0xFFFFFF
        self._use(a, f"left operand of `{op}`"); self._use(b, f"right operand of `{op}`")
        r = self._new(NUM, "r", f"result of `{op}`")
        if isinstance(b, int) and op in ("+", "*"):
            self.stmts.append(self._frag(a) + [f" ~ $([{op}{b & 0xFFFFFF}] ", ("P", r), ")"])
        else:
            self.stmts.append(self._frag(a) + [f" ~ $([{op}] $("] + self._frag(b) + [" ", ("P", r), "))"])
        return r

    def fanout(self, w, n: int):
        """Duplicate a number (or a tuple of numbers) into n wires; inserts the DUP chain {a {b c}}."""
        if not isinstance(w, Wire): return tuple([w] * n) if isinstance(w, int) else self._bad_fan(w)
        if n < 2: raise GlueError(f"{_loc()}: fanout(w, n) needs n >= 2 (got {n}); a single use needs no fanout")
        if not _copyable(w.kind):
            raise GlueError(f"{_loc()}: cannot fanout wire {w._desc()}: a {w.kind} cannot be duplicated safely "
                            f"(HVM2 DUPs are unlabelled). Use it once, or get a copy from a primitive "
                            f"(mc_deliver_keep, mapreduce).")
        self._use(w, f"fanout into {n}")
        ws = [self._new(w.kind, f"{w.hint}{i + 1}", f"copy {i + 1} of `{w.hint}`") for i in range(n)]
        t = [("P", ws[-1])]
        for x in reversed(ws[:-1]): t = ["{", ("P", x), " "] + t + ["}"]
        self.stmts.append([("U", w), " ~ "] + t)
        return tuple(ws)

    def _bad_fan(self, w):
        raise GlueError(f"{_loc()}: fanout needs a wire or an int; got {w!r}")

    def erase(self, *ws):
        """Explicitly drop values that are not needed."""
        for w in ws:
            if isinstance(w, (int, Lit)): continue
            if isinstance(w, (tuple, list)): self.erase(*w); continue
            self._use(w, "erased")
            w.erased = True
            if not w.slot: self.stmts.append([("U", w), " ~ *"])

    def erase_unused(self):
        """Auto-erase helper: when this body finishes (after its return values are taken), every value that is still
        unused is erased instead of raising an error. The erased names are recorded in P.auto_erased."""
        self.auto_erase = True

    def split(self, w, n: int | None = None):
        """Take a tuple wire apart: (a (b c)) -> a, b, c."""
        k = _kind_of(w)
        if n is None:
            if k.tag != "tup": raise GlueError(f"{_loc()}: split needs a tuple wire or an explicit n; `{getattr(w, 'hint', w)}` is {k}")
            kinds = list(k.args)
        else:
            kinds = list(k.args) if k.tag == "tup" and len(k.args) == n else [ANY] * n
        if k.tag == "tup" and len(k.args) != len(kinds):
            raise GlueError(f"{_loc()}: `{w.hint}` is a {len(k.args)}-tuple {k}; cannot split it into {n}")
        self._use(w, "split")
        ws = [self._new(kk, f"{getattr(w, 'hint', 't')}_{i}", f"field {i} of `{getattr(w, 'hint', w)}`")
              for i, kk in enumerate(kinds)]
        self.stmts.append(self._frag(w) + [" ~ "] + self._pfrag(ws))
        return tuple(ws)

    def tup(self, *vals):
        """A tuple value (a (b c)); pass it to a tuple port or return it."""
        return tuple(vals)

    def nil(self, elem=ANY): return Lit("(0 *)", LIST(elem))

    def cons(self, head, tail):
        """List cell (1 (head tail))."""
        kt = _kind_of(tail)
        if kt.tag not in ("list", "any"): raise GlueError(f"{_loc()}: cons tail must be a list; got {kt}")
        self._use(head, "cons head"); self._use(tail, "cons tail")
        r = self._new(LIST(_kind_of(head)), "cell", "cons")
        self.stmts.append([("P", r), " ~ (1 ("] + self._frag(head) + [" "] + self._frag(tail) + ["))"])
        return r

    def as_depth(self, x):
        """Declare that a computed number is a trie depth."""
        if isinstance(x, int): return x
        self._use(x, "as_depth")
        r = self._new(DEPTH, x.hint, f"as_depth({x.hint})")
        self.stmts.append([("U", x), " ~ ", ("P", r)])
        return r

    def hole(self, kind: Kind):
        """A value that will be filled later: returns (value, hole). Use `value` where the result is needed and
        fill `hole` exactly once (d.fill / d.fill_cons, or pass it on). Typical: an output list built in input order
        by a stream walker (the hole travels in the walker state)."""
        cell = [None]
        v = self._new(kind, "val", "d.hole value", slot=False, cell=cell)
        h = self._new(HOLE(kind), "hole", "d.hole", slot=False, cell=cell)
        return v, h

    def fill(self, hole, value):
        """Close a hole with a finished value (e.g. d.nil())."""
        k = _kind_of(hole)
        if k.tag != "hole": raise GlueError(f"{_loc()}: fill needs a hole wire; `{getattr(hole, 'hint', hole)}` is {k}")
        self._check(k.args[0], value, {}, "fill value")
        self._use(hole, "filled"); self._use(value, "fill value")
        self.stmts.append([("U", hole), " ~ "] + self._frag(value))

    def fill_cons(self, hole, head):
        """Put `head` into a list hole and return the hole for the rest of the list."""
        k = _kind_of(hole)
        if k.tag != "hole" or k.args[0].tag not in ("list", "any"):
            raise GlueError(f"{_loc()}: fill_cons needs a hole[list[...]]; got {k}")
        self._use(hole, "fill_cons"); self._use(head, "fill_cons head")
        h2 = self._new(k, "hole", "fill_cons tail hole")
        self.stmts.append([("U", hole), " ~ (1 ("] + self._frag(head) + [" ", ("P", h2), "))"])
        return h2

    def select(self, c, if_true, if_false):
        """c != 0 ? if_true : if_false. Both values are built; the other one is erased (fine for numbers and small
        data; use d.branch when the two cases need different work or would share a wire)."""
        self._check(NUM, c, {}, "select condition")
        env: dict = {}
        kt = _kind_of(if_true)
        self._check(kt, if_false, env, "select if_false (must match if_true)")
        G._sel(self.P.book)
        self._use(c, "select condition"); self._use(if_true, "select if_true"); self._use(if_false, "select if_false")
        r = self._new(kt, "sel", "select")
        self.stmts.append(self._frag(c) + [" ~ ?((@gl_sel2 @gl_sel1s) ("] + self._frag(if_true) + [" ("]
                          + self._frag(if_false) + [" ", ("P", r), ")))"])
        return r

    def branch(self, c, zero, nonzero, *passed):
        """Switch on number c. zero(b, *passed) runs when c == 0; nonzero(b, cm1, *passed) runs otherwise (cm1 = c-1).
        Each branch is its own definition with its own composer `b`; `passed` wires are handed to the branch that
        runs (the other branch's copy is erased automatically). Both branches must return the same number and kinds
        of values; branch() returns them."""
        self._check(NUM, c, {}, "branch condition")
        pk = [_kind_of(p) for p in passed]
        k = self.P._fresh(f"{self.name}_b")
        zname, sname = k + "z", k + "s"
        zt, zk = self.P._compile(zname, f"branch zero case of {self.what}", zero,
                                 [(f"passed[{i}]", kk, None) for i, kk in enumerate(pk)], None)
        st, _ = self.P._compile(sname, f"branch nonzero case of {self.what}", nonzero,
                                [("cm1", NUM, None)] + [(f"passed[{i}]", kk, None) for i, kk in enumerate(pk)],
                                [(f"out{i}", kk, None) for i, kk in enumerate(zk)])
        self.P.book.define(zname, zt); self.P.book.define(sname, st)
        self._use(c, "branch condition")
        for i, p in enumerate(passed): self._use(p, f"branch passed[{i}]")
        outs = [self._new(kk, "br", f"branch result {i}") for i, kk in enumerate(zk)]
        # context = (p1 (p2 ... outs)) where outs is a producer group
        f = self._pfrag(outs) if len(outs) > 0 else ["*"]
        for p in reversed(passed): f = ["("] + self._frag(p) + [" "] + f + [")"]
        self.stmts.append(self._frag(c) + [f" ~ ?((@{zname} @{sname}) "] + f + [")"])
        if not outs: return None
        return outs[0] if len(outs) == 1 else tuple(outs)

    # ---------------------------------------------------------------- close and render
    def _close(self):
        bad = [w for w in self.wires if not w.uses]
        if bad and getattr(self, "auto_erase", False):
            self.erase(*bad)
            self.P.auto_erased.append((self.name, [w.hint for w in bad]))
            bad = []
        if bad:
            lst = "\n".join(f"    {w._desc()}" for w in bad)
            raise GlueError(f"{self.what} (@{self.name}): {len(bad)} value(s) never used:\n{lst}\n"
                            f"  Every value must be used exactly once: pass it where it is needed, or drop it with "
                            f"d.erase(x) (or d.erase_unused() to drop all of them).")
        self.closed = True

    def _render(self, root_frag):
        taken = set()
        for w in self.wires:
            if w.cell[0] is None:
                base = re.sub(r"\W", "", w.hint) or "w"
                if not re.match(r"[A-Za-z]", base): base = "w" + base
                nm, i = base, 1
                while nm in taken: i += 1; nm = f"{base}{i}"
                taken.add(nm); w.cell[0] = nm

        def s(fr):
            out = []
            for x in fr:
                if isinstance(x, str): out.append(x)
                elif x[0] == "P": out.append("*" if x[1].erased else x[1].cell[0])
                else: out.append(x[1].cell[0])
            return "".join(out)
        lines = [s(root_frag)] + ["  & " + s(st) for st in self.stmts]
        return "\n".join(lines)


# ============================================================================ the program
class Program:
    """A net under construction: primitive instances + checked bodies. P.build() returns the HVM text."""

    def __init__(self):
        self.book = Book()
        self.prims: dict[str, Prim] = {}
        self._n = 0
        self.has_prog = False
        self.auto_erased: list = []

    # ---------------------------------------------------------------- internals
    def _fresh(self, base):
        self._n += 1
        return f"{base}{self._n}"

    def _reg(self, name, desc, fn):
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
            raise GlueError(f"{_loc()}: primitive name {name!r} must be letters/digits/_ and start with a letter")
        if name in self.prims and self.prims[name].desc != desc:
            raise GlueError(f"{_loc()}: name clash: `{name}` is already {self.prims[name].desc}; give {desc} another name")
        try:
            return fn()
        except AssertionError as e:
            raise GlueError(f"{_loc()}: name clash while adding {desc}: {e}. Give each primitive instance its own "
                            f"name (and do not name one like another's helper, e.g. `<name>_leaf`).") from None

    def _prim(self, name, entry, desc, sig, **meta):
        p = Prim(entry, desc, sig, **meta)
        self.prims[name] = p
        return p

    def _compile(self, defname, what, fn, params, outs):
        """Compile body function fn into definition text. params: [(label, kind, fields|None)] (fields = a group of
        (name, kind) that is ONE tuple in the net but separate arguments of fn). outs: [(label, kind|None, fields|None)]
        or None (infer from the returned values). Returns (text, list of output kinds)."""
        if isinstance(fn, str):
            return fn.strip(), [ANY] * (len(outs) if outs else 1)
        if not callable(fn):
            raise GlueError(f"{_loc()}: {what} must be a Python function (d, ...) -> value(s); got {fn!r}")
        d = Body(self, defname, what)
        args, root = [], []
        for label, kind, fields in params:
            if kind == "*":
                root.append(("S", None)); continue
            if fields:
                ws = [d._new(k, n, f"argument `{n}` of {what}") for n, k in fields]
                args += ws; root.append(("G", ws))
            else:
                w = d._new(kind, label, f"argument `{label}` of {what}")
                args.append(w); root.append(("G", [w]))
        try:
            sig = inspect.signature(fn)
            pnames = [p.name for p in sig.parameters.values()]
            var = any(p.kind == p.VAR_POSITIONAL for p in sig.parameters.values())
        except (TypeError, ValueError):
            pnames, var = None, True
        labels = []
        params = [x for x in params if x[1] != "*"]
        outs_era = outs is not None and any(o[1] == "*" for o in outs)
        if outs_era: outs = [o for o in outs if o[1] != "*"]
        for label, kind, fields in params:
            labels += [f"{n}:{k}" for n, k in fields] if fields else [f"{label}:{kind}"]
        if pnames is not None and not var and len(pnames) != len(args) + 1:
            raise GlueError(f"wrong arity: {what} is called as f(d, {', '.join(labels)}), i.e. d plus {len(args)} "
                            f"value(s); your function `{fn.__name__}` takes {len(pnames)} parameter(s) "
                            f"({', '.join(pnames)}).")
        if pnames and not var:
            for w, pn in zip(args, pnames[1:]): w.hint = pn
        ret = fn(d, *args)
        if outs is None:
            want = None
            vals = list(ret) if isinstance(ret, tuple) else [ret]
            if ret is None: vals = []
        else:
            m = sum(len(f) if f else 1 for _, _, f in outs)
            if ret is None and m > 0:
                raise GlueError(f"{what}: `{getattr(fn, '__name__', 'body')}` returned None; it must return {m} value(s) "
                                f"({', '.join(l for l, _, _ in outs)}). Did you forget `return`?")
            if m == 1:
                single_tup = outs[0][1] is not None and outs[0][1].tag == "tup" and not outs[0][2]
                vals = [ret] if (single_tup or not isinstance(ret, tuple)) else list(ret)
            else:
                vals = list(ret) if isinstance(ret, (tuple, list)) else [ret]
            if len(vals) != m:
                names = []
                for l, k, f in outs: names += [n for n, _ in f] if f else [l]
                raise GlueError(f"wrong arity: {what} must return {m} value(s) ({', '.join(names)}); "
                                f"`{getattr(fn, '__name__', 'body')}` returned {len(vals)}.")
        kinds = []
        env: dict = {}
        if outs is None:
            for i, v in enumerate(vals):
                kinds.append(_kind_of(v)); d._use(v, f"returned value {i}"); root.append(("V", v))
        else:
            it = iter(vals)
            for label, kind, fields in outs:
                if fields:
                    grp = []
                    for n, k in fields:
                        v = next(it); d._check(k, v, env, f"{what} result `{n}`"); d._use(v, f"returned as `{n}`")
                        kinds.append(_subst(k, env)); grp.append(v)
                    root.append(("V", tuple(grp)))
                else:
                    v = next(it)
                    if kind is not None: d._check(kind, v, env, f"{what} result `{label}`")
                    kinds.append(_kind_of(v) if kind is None or kind.tag in ("any", "var") else _subst(kind, env))
                    d._use(v, f"returned as `{label}`"); root.append(("V", v))
        d._close()
        if outs_era: root.append(("S", None))
        frs = []
        for tag, x in root:
            frs.append(["*"] if tag == "S" else d._pfrag(x) if tag == "G" else d._frag(x))
        if not frs: frs = [["*"]]
        t = frs[-1]
        for f in reversed(frs[:-1]): t = ["("] + f + [" "] + t + [")"]
        return d._render(t), kinds

    # ---------------------------------------------------------------- the root
    def prog(self, prog_id_or_fn, fn=None, inputs=None, out=None):
        """Define @prog. P.prog("t3_degrees", fn): input fields and the output kind come from the contract.
        fn(d, *input_fields) returns the output value."""
        if callable(prog_id_or_fn): fn, pid = prog_id_or_fn, None
        else: pid = prog_id_or_fn
        if pid is not None:
            from ..corpus import load_all
            p = load_all()[pid]
            ik = from_type(p.inp)
            names = [f"in{i}" for i in range(len(ik.args))] if ik.tag == "tup" else ["input"]
            inputs = list(zip(names, ik.args)) if ik.tag == "tup" else [("input", ik)]
            out = from_type(p.out)
        if inputs is None: raise GlueError("prog needs a program id or inputs=[(name, kind), ...]")
        params = [("input", None, inputs)] if len(inputs) > 1 else [(inputs[0][0], inputs[0][1], None)]
        text, _ = self._compile("prog", "@prog" + (f" ({pid})" if pid else ""), fn, params, [("out", out, None)])
        self.book.define("prog", text)
        self.has_prog = True

    def define(self, name, fn, params, outs=None):
        """A free-standing checked helper definition (rarely needed)."""
        text, kinds = self._compile(name, f"@{name}", fn, [(n, k, None) for n, k in params],
                                    None if outs is None else [(f"o{i}", k, None) for i, k in enumerate(outs)])
        self.book.define(name, text)
        return kinds

    def build(self) -> str:
        if not self.has_prog: raise GlueError("no @prog: call P.prog(program_id, fn)")
        text = self.book.text()
        from ..verify import lint_net
        lint = lint_net(text)
        if lint: raise GlueError("the emitted net fails the verifier's static check (a raw-text body?):\n" + lint)
        return text

    def write(self, path, header=""):
        t = self.build()
        with open(path, "w") as f: f.write((f"// {header}\n" if header else "") + t)
        return path

    # ================================================================ primitive factories
    def lg(self):
        """lg: L = number of bits of x. For n >= 1 vertices use L = lg(n-1). (n = 0 needs a guard: see branch.)"""
        return self._reg("lg", "lg", lambda: (G.lg(self.book), self._prim(
            "lg", "lg", "lg", chain(_in("x", NUM), _out("L", DEPTH))))[1])

    def const_trie(self, name, leaf, kind=None):
        """Trie of depth L whose every leaf is the constant `leaf` (an int, or a Lit / closed text like "(0 *)")."""
        if kind is None:
            kind = NUM if isinstance(leaf, int) else (LIST(ANY) if str(leaf).strip() == "(0 *)" else ANY)
        txt = str(leaf.text if isinstance(leaf, Lit) else leaf)
        desc = f"const_trie `{name}` (leaf {txt})"
        return self._reg(name, desc, lambda: (G.const_trie(self.book, name, txt), self._prim(
            name, name, desc, chain(_in("L", DEPTH), _out("t", TRIE(kind)))))[1])

    def empty_adj(self):
        """The empty adjacency trie (every leaf the empty list); use with P.adjacency()."""
        desc = "empty_adj `gl_zl`"
        return self._reg("gl_zl", desc, lambda: (G.const_trie(self.book, "gl_zl", "(0 *)"), self._prim(
            "gl_zl", "gl_zl", desc, chain(_in("L", DEPTH), _out("t", ADJ))))[1])

    def iota_trie(self, name):
        """Leaf i = base + i."""
        desc = f"iota_trie `{name}`"
        return self._reg(name, desc, lambda: (G.iota_trie(self.book, name), self._prim(
            name, name, desc, chain(_in("L", DEPTH), _in("base", NUM, default=0), _out("t", TRIE(NUM)))))[1])

    _NOPAY = {"set1", "inc", "dec"}
    _PAY = {"set", "add", "or", "min", "max"}

    def update(self, name, act, leaf=NUM, payload=NUM):
        """Keyed update: t2 = t with leaf k := act(leaf, P). act: set1 inc dec (no payload port), set add or min max
        (payload P in), push (leaf is a list, P pushed on its front), peek (P is an OUTPUT: a copy of the leaf), or a
        function f(d, leaf, p) -> new leaf (payload=None for a function that takes no payload: f(d, leaf))."""
        desc = f"update `{name}` (act {act if isinstance(act, str) else getattr(act, '__name__', 'fn')})"
        lk = leaf
        if act == "push":
            lk = LIST(payload) if leaf == NUM else leaf
        if isinstance(act, str) and act in G.ACTS:
            body = act
            if act in self._NOPAY: pport = "*"
            elif act == "peek": pport = _out("P", lk, doc="copy of the leaf")
            elif act == "reply": raise GlueError(f"{_loc()}: use P.mc_request for the reply act")
            else: pport = _in("P", payload)
            pk = None if act in self._NOPAY else payload
        elif callable(act):
            if payload is None:
                txt, _ = self._compile(name + "_act", f"act of update `{name}`", act,
                                       [("leaf", lk, None), ("P", "*", None)], [("leaf2", lk, None)])
                pport, pk = "*", None
            else:
                txt, _ = self._compile(name + "_act", f"act of update `{name}`", act,
                                       [("leaf", lk, None), ("p", payload, None)], [("leaf2", lk, None)])
                pport, pk = _in("P", payload), payload
            body = txt
        elif isinstance(act, str):
            body, pport, pk = act, _in("P", payload), payload
        else:
            raise GlueError(f"{_loc()}: act must be one of {sorted(G.ACTS)} or a function")
        return self._reg(name, desc, lambda: (G.update(self.book, name, body), self._prim(
            name, name, desc, chain(_in("t", TRIE(lk)), _in("k", NUM), _in("L", DEPTH), pport, _out("t2", TRIE(lk))),
            payload=pk, leaf=lk))[1])

    def adjacency(self, name="gl_adj"):
        """Push (v w) onto u's list in an adjacency trie. Pair with P.empty_adj()."""
        desc = f"adjacency `{name}`"
        def mk():
            G.const_trie(self.book, "gl_zl", "(0 *)"); G.update(self.book, name, "push")
            return self._prim(name, name, desc, chain(_in("G", ADJ), _in("u", NUM), _in("L", DEPTH),
                                                      (_in("v", NUM), _in("w", NUM, default=0)), _out("G2", ADJ)),
                              payload=TUP(NUM, NUM), leaf=LIST(TUP(NUM, NUM)))
        return self._reg(name, desc, mk)

    def get(self, name):
        """Read leaf k; the rest of the trie is erased (the trie is consumed)."""
        desc = f"get `{name}`"
        return self._reg(name, desc, lambda: (G.get(self.book, name), self._prim(
            name, name, desc, chain(_in("t", TRIE(_V("a"))), _in("k", NUM), _in("L", DEPTH), _out("o", _V("a")))))[1])

    # ---------------------------------------------------------------- traversals
    def _leafparams(self, leaf_kind, index, env):
        ps = [("x", leaf_kind, None)]
        if index: ps.append(("i", NUM, None))
        if env is not None: ps.append(("E", env, None))
        return ps

    def _envcheck(self, env, what):
        if env is not None and not _copyable(env):
            raise GlueError(f"{_loc()}: the environment of {what} is copied to every leaf by DUPs, so it must be "
                            f"numbers or a tuple of numbers; got {env}")

    def _trav_ports(self, lk, index, env):
        ps = [_in("t", TRIE(lk)), _in("L", DEPTH)]
        if index: ps.append(_in("base", NUM, default=0))
        if env is not None: ps.append(_in("E", env))
        return ps

    def reduce(self, name, leaf, op, index=False, env=None, leaf_kind=NUM):
        """o = op over all leaves of leaf(x [, i] [, E]); op in + | & max min. leaf: f(d, x[, i][, E]) -> number.
        index=True adds the leaf index i (= base + position); env=KIND adds an environment E copied to every leaf."""
        if op not in ("+", "|", "&", "^", "*", "max", "min"): raise GlueError(f"{_loc()}: reduce op {op!r}")
        desc = f"reduce `{name}` ({op})"
        self._envcheck(env, desc)
        txt, _ = self._compile(name + "_leaf", f"leaf of {desc}", leaf, self._leafparams(leaf_kind, index, env),
                               [("o", NUM, None)])
        return self._reg(name, desc, lambda: (G.reduce(self.book, name, txt, op, index, env is not None), self._prim(
            name, name, desc, chain(*self._trav_ports(leaf_kind, index, env), _out("o", NUM))))[1])

    def fold(self, name, leaf, acc, index=True, env=None, leaf_kind=NUM):
        """Accumulator threaded right to left through the leaves: leaf f(d, x[, i][, E], acc) -> new acc."""
        desc = f"fold `{name}`"
        self._envcheck(env, desc)
        txt, _ = self._compile(name + "_leaf", f"leaf of {desc}", leaf,
                               self._leafparams(leaf_kind, index, env) + [("acc", acc, None)], [("acc2", acc, None)])
        return self._reg(name, desc, lambda: (G.fold(self.book, name, txt, index, env is not None), self._prim(
            name, name, desc, chain(*self._trav_ports(leaf_kind, index, env), _in("acc", acc), _out("o", acc))))[1])

    def to_list(self, name):
        """First n leaves of a trie as a list in key order (followed by tail, default [])."""
        desc = f"to_list `{name}`"
        a = _V("a")
        return self._reg(name, desc, lambda: (G.to_list(self.book, name), self._prim(
            name, name, desc, chain(_in("t", TRIE(a)), _in("L", DEPTH), "0", _in("n", NUM),
                                    _in("tail", LIST(a), default=Lit("(0 *)", LIST(ANY))), _out("o", LIST(a)))))[1])

    def filter_list(self, name, pred, emit="i", leaf_kind=NUM, env=NUM):
        """List of the index (emit="i") or value (emit="x") of every leaf where pred(d, x, i, E) -> 0/1 is nonzero,
        in key order. Guard indexes >= n in pred yourself (pass n through E)."""
        desc = f"filter_list `{name}`"
        self._envcheck(env, desc)
        txt, _ = self._compile(name + "_p", f"predicate of {desc}", pred,
                               [("x", leaf_kind, None), ("i", NUM, None), ("E", env, None)], [("f", NUM, None)])
        ek = NUM if emit == "i" else leaf_kind
        return self._reg(name, desc, lambda: (G.filter_list(self.book, name, txt, emit), self._prim(
            name, name, desc, chain(_in("t", TRIE(leaf_kind)), _in("L", DEPTH), "0", _in("E", env, default=0),
                                    _in("tail", LIST(ek), default=Lit("(0 *)", LIST(ANY))), _out("o", LIST(ek)))))[1])

    def scatter(self, name, upd, key, leaf_kind=NUM, env=NUM):
        """Every leaf (x, i) applies the keyed update `upd` (a P.update prim) to another trie H:
        key(d, x, i, E) -> (k, P)  (or just k when upd takes no payload). Leaves that must not contribute send the
        combiner's identity to a harmless key."""
        if not isinstance(upd, Prim) or "leaf" not in upd.meta:
            raise GlueError(f"{_loc()}: scatter `{name}` needs an update primitive (P.update(...)); got {upd!r}")
        desc = f"scatter `{name}` via {upd.desc}"
        self._envcheck(env, desc)
        pk = upd.meta["payload"]
        outs = [("k", NUM, None)] + ([("P", pk, None)] if pk is not None else [])
        if isinstance(key, str): txt = key
        else:
            txt, _ = self._compile(name + "_k", f"key of {desc}", key,
                                   [("x", leaf_kind, None), ("i", NUM, None), ("E", env, None)],
                                   outs + ([("P", "*", None)] if pk is None else []))
        hk = TRIE(upd.meta["leaf"])
        return self._reg(name, desc, lambda: (G.scatter(self.book, name, upd.entry, txt), self._prim(
            name, name, desc, chain(_in("t", TRIE(leaf_kind)), _in("L", DEPTH), "0",
                                    (_in("Lh", DEPTH), _in("E", env, default=0)), _in("H", hk), _out("H2", hk))))[1])

    def zip2(self, name, leaf, a=NUM, c=NUM):
        """Leafwise combination of two tries of the same depth: leaf(d, x, y) -> value; returns the new trie."""
        desc = f"zip2 `{name}`"
        txt, ks = self._compile(name + "_leaf", f"leaf of {desc}", leaf, [("x", a, None), ("y", c, None)], None)
        if len(ks) != 1: raise GlueError(f"leaf of {desc} must return exactly one value; returned {len(ks)}")
        return self._reg(name, desc, lambda: (G.zip2(self.book, name, txt), self._prim(
            name, name, desc, chain(_in("a", TRIE(a)), _in("c", TRIE(c)), _in("L", DEPTH), _out("o", TRIE(ks[0])))))[1])

    def zip2e(self, name, leaf, env, a=NUM, c=NUM):
        """zip2 with an environment copied to every leaf: leaf(d, x, y, E) -> value."""
        desc = f"zip2e `{name}`"
        self._envcheck(env, desc)
        txt, ks = self._compile(name + "_leaf", f"leaf of {desc}", leaf,
                                [("x", a, None), ("y", c, None), ("E", env, None)], None)
        if len(ks) != 1: raise GlueError(f"leaf of {desc} must return exactly one value; returned {len(ks)}")
        return self._reg(name, desc, lambda: (G.zip2e(self.book, name, txt), self._prim(
            name, name, desc, chain(_in("a", TRIE(a)), _in("c", TRIE(c)), _in("L", DEPTH), _in("E", env),
                                    _out("o", TRIE(ks[0])))))[1])

    def bcast(self, name, upd):
        """Apply the same keyed update `upd` to every sub-trie hanging from the leaves of an outer trie."""
        desc = f"bcast `{name}` of {upd.desc}"
        hk = TRIE(upd.meta["leaf"])
        pk = upd.meta["payload"] or ANY
        return self._reg(name, desc, lambda: (G.bcast(self.book, name, upd.entry), self._prim(
            name, name, desc, chain(_in("T", TRIE(hk)), _in("Lo", DEPTH),
                                    (_in("Li", DEPTH), (_in("k", NUM), _in("P", pk))), _out("T2", TRIE(hk)))))[1])

    def mapreduce(self, name, leaf, op, index=True, env=None, leaf_kind=NUM):
        """reduce that also rebuilds the trie: leaf(d, x[, i][, E]) -> (new leaf, r); returns (t2, o)."""
        desc = f"mapreduce `{name}` ({op})"
        self._envcheck(env, desc)
        txt, ks = self._compile(name + "_leaf", f"leaf of {desc}", leaf, self._leafparams(leaf_kind, index, env),
                                [("x2", None, None), ("r", NUM, None)])
        return self._reg(name, desc, lambda: (G.mapreduce(self.book, name, txt, op, index, env is not None), self._prim(
            name, name, desc, chain(*self._trav_ports(leaf_kind, index, env), _out("t2", TRIE(ks[0])),
                                    _out("o", NUM))))[1])

    def iterate(self, p, body, state):
        """Sequential while loop: body(d, *state) -> (*new_state, go); repeats while go != 0.
        state = [(name, kind), ...]. d.call(loop, init=(...)) returns the final state fields."""
        desc = f"iterate `{p}`"
        if len(state) < 2: raise GlueError(f"{_loc()}: iterate state needs >= 2 fields (add a counter)")
        txt, _ = self._compile(p + "_body", f"body of {desc}", body, [("S", None, state)],
                               [("S2", None, state), ("go", NUM, None)])
        return self._reg(p + "_it", desc, lambda: (G.iterate(self.book, p, txt), self._prim(
            p + "_it", p + "_it", desc, (_in("init", TUP(*[k for _, k in state]), fields=state),
                                         _out("final", TUP(*[k for _, k in state]), fields=state))))[1])

    # ---------------------------------------------------------------- multicast
    def mc_empty(self, name):
        """Empty request trie."""
        desc = f"mc_empty `{name}`"
        return self._reg(name, desc, lambda: (G.mc_empty(self.book, name), self._prim(
            name, name, desc, chain(_in("L", DEPTH), _out("q", MCQ))))[1])

    def mc_request(self, name, value=NUM):
        """Register a request for key k: returns (r, q2): r will carry value[k] once mc_deliver runs."""
        desc = f"mc_request `{name}`"
        return self._reg(name, desc, lambda: (G.mc_request(self.book, name), self._prim(
            name, name, desc, chain(_in("q", MCQ), _in("k", NUM), _in("L", DEPTH),
                                    _out("r", value, doc="the value at key k, after delivery"), _out("q2", MCQ))))[1])

    def mc_deliver(self, name):
        """Answer every request: value trie v (consumed) -> all registered r wires. Returns nothing."""
        desc = f"mc_deliver `{name}`"
        return self._reg(name, desc, lambda: (G.mc_deliver(self.book, name), self._prim(
            name, name, desc, chain(_in("v", TRIE(NUM)), _in("q", MCQ), _in("L", DEPTH))))[1])

    def mc_deliver_keep(self, name):
        """Like mc_deliver, but returns a copy v2 of the value trie (the safe way to use a numeric trie twice)."""
        desc = f"mc_deliver_keep `{name}`"
        return self._reg(name, desc, lambda: (G.mc_deliver_keep(self.book, name), self._prim(
            name, name, desc, chain(_in("v", TRIE(NUM)), _in("q", MCQ), _in("L", DEPTH), _out("v2", TRIE(NUM)))))[1])

    # ---------------------------------------------------------------- walker, loops
    def stream(self, p, step, fin, state, elem=EDGE, k=16):
        """List walker. state = [(name, kind), ...]; elem = the list element kind (a tuple kind is unpacked into
        separate arguments). step(d, *state, *elem_fields) -> new state fields; fin(d, *state) -> result.
        d.call(w, list=..., init=(state values...)) returns fin's result."""
        desc = f"stream `{p}`"
        ef = [(f"e{i}", k_) for i, k_ in enumerate(elem.args)] if elem.tag == "tup" else None
        sparams = [("S", None, state)] + [("elem", elem if ef is None else None, ef)]
        stxt, _ = self._compile(p + "_step", f"step of {desc}", step, sparams, [("S2", None, state)])
        ftxt, fk = self._compile(p + "_fin", f"fin of {desc}", fin, [("S", None, state)], None)
        if len(fk) != 1: raise GlueError(f"fin of {desc} must return exactly one value (the result); returned {len(fk)}")
        stk = TUP(*[kk for _, kk in state]) if len(state) > 1 else state[0][1]
        return self._reg(p + "_blk", desc, lambda: (G.stream(self.book, p, k, stxt, ftxt), self._prim(
            p + "_blk", p + "_blk", desc, chain(_in("list", LIST(elem)),
                                               _in("init", stk, fields=state if len(state) > 1 else None),
                                               _out("out", fk[0]))))[1])

    def frontier(self, p, act, msg, comb, ident, state=NUM, message=NUM, env=NUM, env_default=None):
        """Frontier fixpoint. act(d, X, dv, c) -> (d2, flag, m) runs at every vertex each round (dv = its state,
        c = its combined incoming message, X = the environment); flagged vertices send msg(d, m, w) -> r along every
        out-edge (v w), combined at v with `comb` (an update act name or f(d, leaf, p)) over identity `ident`. Stops
        after a round with no flag. d.call(loop, G=adj, D=state trie, C=first messages, L=depth, X=env) -> final D."""
        desc = f"frontier `{p}`"
        self._envcheck(env, desc)
        atxt, ak = self._compile(p + "_act", f"act of {desc}", act,
                                 [("X", env, None), ("dv", state, None), ("c", message, None)],
                                 [("d2", state, None), ("flag", NUM, None), ("m", None, None)])
        mtxt, _ = self._compile(p + "_msg", f"msg of {desc}", msg, [("m", ak[2], None), ("w", NUM, None)],
                                [("r", message, None)])
        if callable(comb):
            ctxt, _ = self._compile(p + "_cu_act", f"combiner of {desc}", comb, [("leaf", message, None), ("p", message, None)],
                                    [("leaf2", message, None)])
        else: ctxt = comb
        ident_t = str(ident.text if isinstance(ident, Lit) else ident)
        return self._reg(p + "_loop", desc, lambda: (G.frontier(self.book, p, atxt, mtxt, ctxt, ident_t), self._prim(
            p + "_loop", p + "_loop", desc,
            (chain(_in("G", ADJ), _in("D", TRIE(state)), _in("C", TRIE(message)), _in("L", DEPTH),
                   _in("X", env, default=env_default)), _out("D2", TRIE(state)))))[1])

    def relax(self, p, maximize=False):
        """Min-plus relaxation on frontier (shortest paths with a budget X, default none; min-label components).
        maximize=True: max-label propagation over edges with w in {0,1} (message d*w). Same ports as frontier."""
        desc = f"relax `{p}`" + (" (max)" if maximize else "")
        return self._reg(p + "_loop", desc, lambda: (G.relax(self.book, p, maximize), self._prim(
            p + "_loop", p + "_loop", desc,
            (chain(_in("G", ADJ), _in("D", TRIE(NUM)), _in("C", TRIE(NUM)), _in("L", DEPTH),
                   _in("X", NUM, default=INF if not maximize else 0, doc="budget (min only)")),
             _out("D2", TRIE(NUM)))))[1])

    def sssp(self, p):
        """Single-source shortest paths: D[v] = distance from s (INF if unreachable or > budget); s >= n gives all INF."""
        desc = f"sssp `{p}`"
        return self._reg(p + "_sssp", desc, lambda: (G.sssp(self.book, p), self._prim(
            p + "_sssp", p + "_sssp", desc,
            chain(_in("n", NUM), _in("s", NUM), _in("L", DEPTH), _in("budget", NUM, default=INF), _in("G", ADJ),
                  _out("D", TRIE(NUM)))))[1])

    def sel_helpers(self):
        G._sel(self.book)
