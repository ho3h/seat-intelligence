"""Parse and print HVM2 text nets. Trees are tuples: ('con',a,b) ('dup',a,b) ('opr',a,b) ('swi',a,b)
('era',) ('num',text) ('ref',name) ('var',name). A def is (name, root_tree, [(par_flag, left, right), ...])."""
from __future__ import annotations
import re

_TOK = re.compile(r"//[^\n]*|\s+|(\$\(|\?\(|&!|[()\{\}&~=*]|@[\w/]+|\[[^\]]*\]\d*|[-+]?\d[\w.]*|[A-Za-z_][\w]*)")


def tokens(text):
    out = []
    for m in _TOK.finditer(text):
        if m.group(1): out.append(m.group(1))
    return out


def parse_book(text):
    toks = tokens(text); pos = 0
    import sys; sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

    def tree():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t == "(": a = tree(); b = tree(); pos += 1; return ("con", a, b)
        if t == "{": a = tree(); b = tree(); pos += 1; return ("dup", a, b)
        if t == "$(": a = tree(); b = tree(); pos += 1; return ("opr", a, b)
        if t == "?(": a = tree(); b = tree(); pos += 1; return ("swi", a, b)
        if t == "*": return ("era",)
        if t.startswith("@"): return ("ref", t[1:])
        if t[0].isdigit() or t[0] in "+-[": return ("num", t)
        return ("var", t)

    defs = {}
    order = []
    while pos < len(toks):
        assert toks[pos].startswith("@"), toks[pos:pos + 3]
        name = toks[pos][1:]; pos += 1; assert toks[pos] == "="; pos += 1
        root = tree(); reds = []
        while pos < len(toks) and toks[pos] in ("&", "&!"):
            par = toks[pos] == "&!"; pos += 1
            a = tree(); assert toks[pos] == "~"; pos += 1; b = tree(); reds.append((par, a, b))
        defs[name] = (root, reds); order.append(name)
    return defs, order


def show(t):
    k = t[0]
    if k == "con": return f"({show(t[1])} {show(t[2])})"
    if k == "dup": return "{" + f"{show(t[1])} {show(t[2])}" + "}"
    if k == "opr": return f"$({show(t[1])} {show(t[2])})"
    if k == "swi": return f"?({show(t[1])} {show(t[2])})"
    if k == "era": return "*"
    if k == "ref": return "@" + t[1]
    return t[1]


def print_book(defs, order):
    out = []
    for n in order:
        root, reds = defs[n]
        out.append(f"@{n} = {show(root)}" + "".join(f"\n  &{'!' if p else ''} {show(a)} ~ {show(b)}" for p, a, b in reds))
    return "\n\n".join(out) + "\n"


def size(t):
    """Number of nodes (leaves count 1)."""
    k = t[0]
    return 1 + (size(t[1]) + size(t[2]) if k in ("con", "dup", "opr", "swi") else 0)


def var_counts(t, acc=None):
    acc = {} if acc is None else acc
    if t[0] == "var": acc[t[1]] = acc.get(t[1], 0) + 1
    elif t[0] in ("con", "dup", "opr", "swi"): var_counts(t[1], acc); var_counts(t[2], acc)
    return acc
