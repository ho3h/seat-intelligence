"""Interface types and their net encodings.

Tag-first constructors, the same convention as Bend's tagged tuples. NOTE: Bend 0.2.38 compiles
List/Cons to a lambda encoding (see `bend gen-hvm`), not to these tuples, so the B1 arm needs a
thin adapter to and from this interface before it can be scored on the same contract.

  u24        a native number, arithmetic mod 2^24
  list[T]    Nil = (0 *)    Cons = (1 (head tail))
  tuple[..]  (a (b c))      right-nested constructors, last element unwrapped
"""
from __future__ import annotations
from dataclasses import dataclass
import re

MASK = (1 << 24) - 1
NODE_BUDGET = 3000  # HVM2 caps a definition at 4095 nodes; stay well inside


@dataclass(frozen=True)
class U24:
    def __str__(self): return "u24"


@dataclass(frozen=True)
class List:
    elem: object
    def __str__(self): return f"list[{self.elem}]"


@dataclass(frozen=True)
class Tup:
    elems: tuple
    def __str__(self): return "tuple[" + ", ".join(map(str, self.elems)) + "]"


@dataclass(frozen=True)
class Rec:
    """Placeholder for the enclosing Adt inside its own constructor fields."""
    def __str__(self): return "self"


@dataclass(frozen=True)
class Adt:
    """Algebraic data type. ctors is a tuple of constructors; each constructor is a tuple of field types
    (Rec() = the type itself). A value is (ctor_index, field1, field2, ...).
    Encoded as (ctor_index payload) with payload = right-nested fields, `*` for no fields, the bare field for one.
    List is Adt with Nil=(), Cons=(elem, Rec) -- and the List class above is kept for its chunking.
    """
    name: str
    ctors: tuple
    def __str__(self):
        cs = " | ".join(f"{i}:" + ("(" + ", ".join(map(str, c)) + ")" if c else "()") for i, c in enumerate(self.ctors))
        return f"{self.name}<{cs}>"


u24 = U24()
REC = Rec()
def adt(name, *ctors): return Adt(name, tuple(tuple(c) for c in ctors))
def tree_of(t, name="tree"):
    """Leaf | Node(left, value, right)."""
    return adt(name, (), (REC, t, REC))
def list_of(t): return List(t)
def tup(*ts): return Tup(tuple(ts))


# ---------------------------------------------------------------- encoding
def _enc(v, t, defs, tag):
    """Return (text, nodes) for value v of type t. Long lists spill into ref chunks."""
    if isinstance(t, U24):
        assert isinstance(v, int) and 0 <= v <= MASK, f"bad u24 {v!r}"
        return str(v), 0
    if isinstance(t, Tup):
        assert len(v) == len(t.elems)
        parts = [_enc(x, et, defs, tag) for x, et in zip(v, t.elems)]
        text, nodes = parts[-1]
        for ptxt, pn in reversed(parts[:-1]):
            text, nodes = f"({ptxt} {text})", nodes + pn + 1
        return text, nodes
    if isinstance(t, List):
        elems = [_enc(x, t.elem, defs, tag) for x in v]
        # cells are consumed left to right; group into chunks under the node budget
        chunks, cur, cur_nodes = [], [], 0
        for txt, n in elems:
            if cur and cur_nodes + n + 2 > NODE_BUDGET:
                chunks.append(cur); cur, cur_nodes = [], 0
            cur.append(txt); cur_nodes += n + 2
        chunks.append(cur)
        tail = "(0 *)"
        for i in range(len(chunks) - 1, -1, -1):
            body = "".join(f"(1 ({x} " for x in chunks[i]) + tail + "))" * len(chunks[i])
            if i == 0:
                return body, 2 * len(chunks[0]) + sum(n for _, n in elems[:len(chunks[0])])
            name = f"__{tag}_{len(defs)}"
            defs.append(f"@{name} = {body}")
            tail = f"@{name}"
    if isinstance(t, Adt):
        return _enc_adt(v, t, t, defs, tag)
    raise TypeError(t)


SPILL = 1200  # subtrees bigger than this many nodes move into their own definition


def _enc_adt(v, t, whole, defs, tag):
    idx, fields = v[0], v[1:]
    ftypes = t.ctors[idx]
    assert len(fields) == len(ftypes), f"{t.name} ctor {idx} wants {len(ftypes)} fields, got {len(fields)}"
    parts = []
    for x, ft in zip(fields, ftypes):
        if isinstance(ft, Rec):
            txt, n = _enc_adt(x, whole, whole, defs, tag)
            if n > SPILL:
                name = f"__{tag}_{len(defs)}"
                defs.append(f"@{name} = {txt}")
                txt, n = f"@{name}", 0
            parts.append((txt, n))
        else:
            parts.append(_enc(x, ft, defs, tag))
    if not parts: payload, pn = "*", 0
    else:
        payload, pn = parts[-1]
        for ptxt, n in reversed(parts[:-1]):
            payload, pn = f"({ptxt} {payload})", pn + n + 1
    return f"({idx} {payload})", pn + 1


def encode(v, t, tag="in"):
    """-> (root_tree_text, [def_text, ...])"""
    defs: list[str] = []
    text, _ = _enc(v, t, defs, tag)
    return text, defs


# ---------------------------------------------------------------- decoding
_TOK = re.compile(r"\s*(\(|\)|\*|[^\s()*]+)")


class DecodeError(Exception):
    pass


def _parse_tree(s):
    toks = _TOK.findall(s)
    pos = 0

    def go():
        nonlocal pos
        if pos >= len(toks): raise DecodeError("truncated output")
        t = toks[pos]; pos += 1
        if t == "(":
            a = go(); b = go()
            if pos >= len(toks) or toks[pos] != ")": raise DecodeError("malformed constructor")
            pos += 1
            return ("con", a, b)
        if t == "*": return ("era",)
        if re.fullmatch(r"\d+", t): return ("num", int(t))
        return ("other", t)

    import sys
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))
    tree = go()
    if pos != len(toks): raise DecodeError("trailing tokens in output")
    return tree


def _dec(tr, t):
    if isinstance(t, U24):
        if tr[0] != "num": raise DecodeError(f"expected u24, got {_show(tr)}")
        return tr[1]
    if isinstance(t, Tup):
        out = []
        for et in t.elems[:-1]:
            if tr[0] != "con": raise DecodeError(f"expected tuple constructor, got {_show(tr)}")
            out.append(_dec(tr[1], et)); tr = tr[2]
        out.append(_dec(tr, t.elems[-1]))
        return tuple(out)
    if isinstance(t, List):
        out = []
        while True:
            if tr[0] != "con" or tr[1] != ("num", 0) and tr[1] != ("num", 1):
                raise DecodeError(f"expected list cell, got {_show(tr)}")
            if tr[1] == ("num", 0):
                if tr[2] != ("era",): raise DecodeError(f"malformed Nil payload {_show(tr[2])}")
                return out
            cell = tr[2]
            if cell[0] != "con": raise DecodeError(f"malformed Cons payload {_show(cell)}")
            out.append(_dec(cell[1], t.elem)); tr = cell[2]
    if isinstance(t, Adt):
        return _dec_adt(tr, t, t)
    raise TypeError(t)


def _dec_adt(tr, t, whole):
    if tr[0] != "con" or tr[1][0] != "num" or tr[1][1] >= len(t.ctors):
        raise DecodeError(f"expected {t.name} constructor, got {_show(tr)}")
    idx = tr[1][1]; ftypes = t.ctors[idx]; pay = tr[2]
    if not ftypes:
        if pay != ("era",): raise DecodeError(f"malformed payload of nullary ctor {idx}: {_show(pay)}")
        return (idx,)
    out = []
    for i, ft in enumerate(ftypes):
        last = i == len(ftypes) - 1
        if last: node = pay
        else:
            if pay[0] != "con": raise DecodeError(f"malformed {t.name} payload {_show(pay)}")
            node, pay = pay[1], pay[2]
        out.append(_dec_adt(node, whole, whole) if isinstance(ft, Rec) else _dec(node, ft))
    return (idx, *out)


def _show(tr, limit=160):
    def go(x):
        if x[0] == "con": return f"({go(x[1])} {go(x[2])})"
        if x[0] == "era": return "*"
        return str(x[1])
    s = go(tr) if len(str(tr)) < 20000 else "<large>"
    return s if len(s) <= limit else s[:limit] + "…"


def decode(result_text, t):
    return _dec(_parse_tree(result_text), t)


def describe(t) -> str:
    return str(t)
