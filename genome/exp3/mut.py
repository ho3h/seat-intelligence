"""Mutation operators on parsed HVM2 books (genome.netast representation: defs = {name: (root, [(par, a, b), ...])}).

Every operator is (sites(defs) -> list, apply(defs, site) -> new defs or None). Operators never mutate their input.
Targeted peepholes (T*) are exact or usually exact; random structural ones (R*) are almost always wrong and rely on the
verifier. Nothing is trusted: every candidate is judged by the hidden-suite verifier.
"""
from __future__ import annotations
import itertools, re
from ..netast import parse_book, print_book, size
from ..opt import reduce_def, call_graph, recursive, optimize

KIDS = ("con", "dup", "opr", "swi")
_fresh = itertools.count()
COMM = {"+", "*", "&", "|", "^", "=", "!"}
OPS = ["+", "-", "*", "/", "%", "=", "!", "<", ">", "&", "|", "^", "<<", ">>"]
SYM_RE = re.compile(r"^\[(<<|>>|[-+*/%=!<>&|^])\]$")
PRE_RE = re.compile(r"^\[(:?)(<<|>>|[-+*/%=!<>&|^])(\d+|0x[0-9A-Fa-f]+)\]$")
DEC = re.compile(r"^(\d+|0x[0-9A-Fa-f]+)$")


def lv(s):
    return int(s, 16) if s.startswith("0x") else int(s)
M24 = (1 << 24) - 1


# ------------------------------------------------------------------ tree plumbing
def get(t, path):
    for i in path: t = t[i]
    return t


def put(t, path, new):
    if not path: return new
    i = path[0]
    return t[:i] + (put(t[i], path[1:], new),) + t[i + 1:]


def nodes(t, path=()):
    yield path, t
    if t[0] in KIDS:
        yield from nodes(t[1], path + (1,))
        yield from nodes(t[2], path + (2,))


def stmts(d):
    """(slot, tree) for root (slot ('r',)) and each redex side (slot ('x', i, side))."""
    root, reds = d
    yield ("r",), root
    for i, (_, a, b) in enumerate(reds):
        yield ("x", i, 1), a
        yield ("x", i, 2), b


def get_slot(d, slot):
    root, reds = d
    return root if slot[0] == "r" else reds[slot[1]][slot[2]]


def set_slot(d, slot, new):
    root, reds = d
    if slot[0] == "r": return (new, reds)
    reds = list(reds); r = list(reds[slot[1]]); r[slot[2]] = new; reds[slot[1]] = tuple(r)
    return (root, reds)


def var_counts(t, acc):
    if t[0] == "var": acc[t[1]] = acc.get(t[1], 0) + 1
    elif t[0] in KIDS: var_counts(t[1], acc); var_counts(t[2], acc)
    return acc


def def_vars(d):
    acc = {}
    for _, t in stmts(d): var_counts(t, acc)
    return acc


def rename(t, suf):
    if t[0] == "var": return ("var", t[1] + suf)
    if t[0] in KIDS: return (t[0], rename(t[1], suf), rename(t[2], suf))
    return t


def has(t, k):
    return t[0] == k or (t[0] in KIDS and (has(t[1], k) or has(t[2], k)))


def def_has(d, k):
    return any(has(t, k) for _, t in stmts(d))


def total_size(defs):
    return sum(size(t) for d in defs.values() for _, t in stmts(d))


def fresh_name(defs, base):
    n = base
    k = 0
    while n in defs: k += 1; n = f"{base}{k}"
    return n


def lint(defs, native: bool):
    for name, d in defs.items():
        for v, c in def_vars(d).items():
            if c != 2: return f"{name}: wire {v} x{c}"
        root, reds = d
        for _, a, b in reds:
            if a[0] == "var" and b[0] == "var" and a[1] == b[1]: return f"{name}: self loop"
    refs = set()
    for d in defs.values():
        for _, t in stmts(d):
            for _, n in nodes(t):
                if n[0] == "ref": refs.add(n[1])
    miss = [r for r in refs if r not in defs and not r.startswith("__")]
    if miss: return f"undefined {miss[:3]}"
    if "prog" not in defs: return "no prog"
    return None


def prune(defs, order):
    """Drop definitions not reachable from @prog."""
    cg = call_graph(defs)
    seen, st = set(), ["prog"]
    while st:
        n = st.pop()
        if n in seen or n not in defs: continue
        seen.add(n); st.extend(cg[n])
    return {n: defs[n] for n in defs if n in seen}, [n for n in order if n in seen]


def reduce_all(defs, names):
    out = dict(defs)
    for n in names:
        r, rd, _ = reduce_def(*out[n]); out[n] = (r, rd)
    return out


# ------------------------------------------------------------------ number helpers
def opnum(sym, a, b):
    if sym in ("/", "%") and b == 0: return None
    f = {"+": a + b, "-": a - b, "*": a * b, "/": a // b if b else 0, "%": a % b if b else 0, "=": int(a == b), "!": int(a != b),
         "<": int(a < b), ">": int(a > b), "&": a & b, "|": a | b, "^": a ^ b, "<<": a << (b % 24), ">>": a >> (b % 24)}[sym]
    return f & M24


# ------------------------------------------------------------------ T1 preset operand: $([op] $(k r)) -> $([:op k] r)
def preset_sites(defs):
    out = []
    for n, d in defs.items():
        for slot, t in stmts(d):
            for path, x in nodes(t):
                if x[0] == "opr" and x[1][0] == "num" and SYM_RE.match(x[1][1]) and x[2][0] == "opr" and x[2][1][0] == "num" and DEC.match(x[2][1][1]):
                    out.append((n, slot, path))
    return out


def preset_apply(defs, site):
    n, slot, path = site; d = defs[n]; t = get_slot(d, slot); x = get(t, path)
    sym = SYM_RE.match(x[1][1]).group(1); k = x[2][1][1]
    lit = f"[{'' if sym in COMM else ':'}{sym}{k}]"
    return {**defs, n: set_slot(d, slot, put(t, path, ("opr", ("num", lit), x[2][2])))}


# ------------------------------------------------------------------ T2 literal-first operand / constant folding in redexes
def litfirst_sites(defs):
    out = []
    for n, (root, reds) in defs.items():
        for i, (_, a, b) in enumerate(reds):
            for s, (x, y) in enumerate(((a, b), (b, a))):
                if x[0] == "num" and DEC.match(x[1]) and y[0] == "opr" and y[1][0] == "num":
                    if SYM_RE.match(y[1][1]) and y[2][0] == "opr": out.append((n, i, s))
                    elif PRE_RE.match(y[1][1]): out.append((n, i, s))
    return out


def litfirst_apply(defs, site):
    n, i, s = site; root, reds = defs[n]; par, a, b = reds[i]
    x, y = (a, b) if s == 0 else (b, a)
    k = lv(x[1]); reds = list(reds)
    m = SYM_RE.match(y[1][1])
    if m:
        sym = m.group(1); other, r = y[2][1], y[2][2]
        if other[0] == "num" and DEC.match(other[1]):
            v = opnum(sym, k, lv(other[1]))
            if v is None: return None
            reds[i] = (par, r, ("num", str(v)))
        else:
            reds[i] = (par, other, ("opr", ("num", f"[{sym}{k}]"), r))  # [op k] applied to n computes k op n
    else:
        flip, sym, c = PRE_RE.match(y[1][1]).groups()
        v = opnum(sym, k, lv(c)) if flip else opnum(sym, lv(c), k)
        if v is None: return None
        reds[i] = (par, y[2], ("num", str(v)))
    r2, rd2, _ = reduce_def(root, reds)
    return {**defs, n: (r2, rd2)}


# ------------------------------------------------------------------ T3 zero test feeding a switch -> switch directly
def _zero_kind(y):
    """y is the OPR tree the tested value meets. Returns (kind, z) with kind 'eq' (z = h==0) or 'ne' (z = h!=0)."""
    if y[0] != "opr" or y[1][0] != "num": return None
    s = y[1][1]
    m = SYM_RE.match(s)
    if m and y[2][0] == "opr" and y[2][1][0] == "num" and DEC.match(y[2][1][1]):
        sym, k, z = m.group(1), lv(y[2][1][1]), y[2][2]
    else:
        m = PRE_RE.match(s)
        if not m: return None
        flip, sym, k = m.groups(); k = lv(k); z = y[2]
        if not flip:  # computes k op h
            sym = {"<": ">", ">": "<"}.get(sym, sym) if sym in ("<", ">", "=", "!") else None
            if sym is None: return None
    if (sym, k) in (("=", 0), ("<", 1)): kind = "eq"
    elif (sym, k) in (("!", 0), (">", 0)): kind = "ne"
    else: return None
    if z[0] == "var": return kind, z[1]
    if z[0] == "swi" and z[1][0] == "con": return kind, z
    return None


def eqz_sites(defs):
    out = []
    for n, (root, reds) in defs.items():
        cnt = def_vars((root, reds))
        for i, (_, a, b) in enumerate(reds):
            for s, (x, y) in enumerate(((a, b), (b, a))):
                zk = _zero_kind(y)
                if not zk or not isinstance(zk[1], str) or cnt.get(zk[1]) != 2: continue
                for j, (_, c, e) in enumerate(reds):
                    if j == i: continue
                    for s2, (u, w) in enumerate(((c, e), (e, c))):
                        if u == ("var", zk[1]) and w[0] == "swi" and w[1][0] == "con": out.append((n, i, s, j, s2))
    return out


def eqz_apply(defs, site):
    n, i, s, j, s2 = site; root, reds = defs[n]
    a, b = reds[i][1:]; x, y = (a, b) if s == 0 else (b, a)
    kind, z = _zero_kind(y)
    c, e = reds[j][1:]; w = e if s2 == 0 else c
    defs = dict(defs)
    sw = _zswitch(defs, kind, w)
    if sw is None: return None
    nr = [r for k, r in enumerate(reds) if k not in (i, j)] + [(reds[i][0], x, sw)]
    defs[n] = (root, nr)
    return defs


def _zswitch(defs, kind, w):
    """Given the switch tree w that consumed the boolean, build the switch that consumes the tested number directly.
    Adds helper definitions to defs (mutates the passed dict)."""
    A, Bb = w[1][1], w[1][2]; ctx = w[2]

    def strip_era(t):  # zero-branch version of a branch that expects (0 ctx) with a leading *
        if t[0] == "con" and t[1][0] == "era": return t[2]
        if t[0] == "ref" and t[1] in defs:
            r0, rd0 = defs[t[1]]
            if r0[0] == "con" and r0[1][0] == "era":
                nn = fresh_name(defs, t[1] + "_z"); defs[nn] = (r0[2], rd0); return ("ref", nn)
        return None

    def add_era(t):
        if t[0] == "ref" and t[1] in defs:
            r0, rd0 = defs[t[1]]; nn = fresh_name(defs, t[1] + "_s"); defs[nn] = (("con", ("era",), r0), rd0); return ("ref", nn)
        return ("con", ("era",), t)

    def swallows(t):
        if t[0] == "con": return t[1][0] == "era"
        return t[0] == "ref" and t[1] in defs and defs[t[1]][0][0] == "con" and defs[t[1]][0][1][0] == "era"

    if kind == "eq":
        zb = strip_era(Bb)
        if zb is None: return None
        sw = ("swi", ("con", zb, add_era(A)), ctx)
    else:
        if not swallows(Bb): return None
        sw = ("swi", ("con", A, Bb), ctx)
    return sw


def eqzi_sites(defs):
    return [(n, slot, path) for n, d in defs.items() for slot, t in stmts(d) for path, x in nodes(t)
            if x[0] == "opr" and (lambda zk: zk is not None and not isinstance(zk[1], str))(_zero_kind(x))]


def eqzi_apply(defs, site):
    n, slot, path = site; d = defs[n]; t = get_slot(d, slot); x = get(t, path)
    kind, w = _zero_kind(x)
    defs = dict(defs)
    sw = _zswitch(defs, kind, w)
    if sw is None: return None
    defs[n] = set_slot(d, slot, put(t, path, sw))
    return defs


# ------------------------------------------------------------------ T2b number meets an operator whose first operand is pending: do the flip statically
def numopr_sites(defs):
    return [(n, i, s) for n, (root, reds) in defs.items() for i, (_, a, b) in enumerate(reds)
            for s, (x, y) in enumerate(((a, b), (b, a))) if x[0] == "num" and y[0] == "opr" and y[1][0] != "num"]


def numopr_apply(defs, site):
    n, i, s = site; root, reds = defs[n]; par, a, b = reds[i]
    x, y = (a, b) if s == 0 else (b, a)
    reds = list(reds); reds[i] = (par, y[1], ("opr", x, y[2]))
    r2, rd2, _ = reduce_def(root, reds)
    return {**defs, n: (r2, rd2)}


# ------------------------------------------------------------------ T4 duplicate-then-erase: {a *} -> a
def duperase_sites(defs):
    return [(n, slot, path) for n, d in defs.items() for slot, t in stmts(d) for path, x in nodes(t)
            if x[0] == "dup" and (x[1][0] == "era" or x[2][0] == "era")]


def duperase_apply(defs, site):
    n, slot, path = site; d = defs[n]; t = get_slot(d, slot); x = get(t, path)
    keep = x[2] if x[1][0] == "era" else x[1]
    d2 = set_slot(d, slot, put(t, path, keep))
    r, rd, _ = reduce_def(*d2)
    return {**defs, n: (r, rd)}


# ------------------------------------------------------------------ T5 inline a call `& @f ~ (..)` (f may be recursive: one unrolling)
def call_sites(defs):
    return [(n, i, s) for n, (root, reds) in defs.items() for i, (_, a, b) in enumerate(reds)
            for s, (x, y) in enumerate(((a, b), (b, a))) if x[0] == "ref" and x[1] in defs and y[0] in KIDS]


def call_apply(defs, site, dup_guard=True):
    n, i, s = site; root, reds = defs[n]; par, a, b = reds[i]
    x, y = (a, b) if s == 0 else (b, a)
    froot, freds = defs[x[1]]
    suf = f"_q{next(_fresh)}"
    nr = list(reds[:i]) + list(reds[i + 1:]) + [(par, rename(froot, suf), y)] + [(p, rename(u, suf), rename(v, suf)) for p, u, v in freds]
    r2, rd2, _ = reduce_def(root, nr)
    return {**defs, n: (r2, rd2)}


# ------------------------------------------------------------------ T6 inline a tree-only definition at a leaf (e.g. a switch branch)
def leaf_sites(defs):
    out = []
    for n, d in defs.items():
        for slot, t in stmts(d):
            for path, x in nodes(t):
                if path and x[0] == "ref" and x[1] in defs and not defs[x[1]][1] and size(defs[x[1]][0]) <= 40:
                    out.append((n, slot, path))
    return out


def leaf_apply(defs, site):
    n, slot, path = site; d = defs[n]; t = get_slot(d, slot); x = get(t, path)
    body = rename(defs[x[1]][0], f"_q{next(_fresh)}")
    return {**defs, n: set_slot(d, slot, put(t, path, body))}


# ------------------------------------------------------------------ T7 whole-book exact optimizer (genome/opt.py) with larger inlining
def opt_apply(defs, order, max_size=40):
    txt, _ = optimize(print_book(defs, order), max_size=max_size, rounds=3)
    return parse_book(txt)[0]


# ------------------------------------------------------------------ R* random structural mutations (verifier-filtered)
def var_sites(defs):
    return [(n, slot, path) for n, d in defs.items() for slot, t in stmts(d) for path, x in nodes(t) if x[0] == "var"]


def rewire_apply(defs, rng):
    names = [n for n in defs if len(def_vars(defs[n])) >= 2]
    if not names: return None
    n = rng.choice(names); d = defs[n]
    occ = [(slot, path, x[1]) for slot, t in stmts(d) for path, x in nodes(t) if x[0] == "var"]
    (s1, p1, v1), (s2, p2, v2) = rng.sample(occ, 2)
    if v1 == v2: return None
    d = set_slot(d, s1, put(get_slot(d, s1), p1, ("var", v2)))
    d = set_slot(d, s2, put(get_slot(d, s2), p2, ("var", v1)))
    return {**defs, n: d}


def cutwire_apply(defs, rng):
    names = [n for n in defs if def_vars(defs[n])]
    n = rng.choice(names); d = defs[n]; v = rng.choice(sorted(def_vars(d)))
    occ = [(slot, path) for slot, t in stmts(d) for path, x in nodes(t) if x == ("var", v)]
    for slot, path in occ: d = set_slot(d, slot, put(get_slot(d, slot), path, ("era",)))
    r, rd, _ = reduce_def(*d)
    return {**defs, n: (r, rd)}


def _num_sites(defs, pred):
    return [(n, slot, path) for n, d in defs.items() for slot, t in stmts(d) for path, x in nodes(t) if x[0] == "num" and pred(x[1])]


def opsym_apply(defs, rng):
    st = _num_sites(defs, lambda s: bool(SYM_RE.match(s) or PRE_RE.match(s)))
    if not st: return None
    n, slot, path = rng.choice(st); d = defs[n]; t = get_slot(d, slot); s = get(t, path)[1]
    m = SYM_RE.match(s)
    if m: new = f"[{rng.choice(OPS)}]"
    else:
        flip, sym, k = PRE_RE.match(s).groups()
        new = f"[{rng.choice(['', ':'])}{rng.choice(OPS)}{k}]" if rng.random() < .7 else f"[{':' if not flip else ''}{sym}{k}]"
    if new == s: return None
    return {**defs, n: set_slot(d, slot, put(t, path, ("num", new)))}


def lit_apply(defs, rng):
    st = _num_sites(defs, lambda s: bool(DEC.match(s) or PRE_RE.match(s)))
    if not st: return None
    n, slot, path = rng.choice(st); d = defs[n]; t = get_slot(d, slot); s = get(t, path)[1]
    if DEC.match(s): k = lv(s); new = str(max(0, rng.choice([k - 1, k + 1, 0, 1])))
    else:
        flip, sym, k = PRE_RE.match(s).groups(); k = lv(k); new = f"[{flip}{sym}{max(0, rng.choice([k - 1, k + 1, 0, 1]))}]"
    if new == s: return None
    return {**defs, n: set_slot(d, slot, put(t, path, ("num", new)))}


def swapkids_apply(defs, rng):
    st = [(n, slot, path) for n, d in defs.items() for slot, t in stmts(d) for path, x in nodes(t) if x[0] in ("con", "opr")]
    if not st: return None
    n, slot, path = rng.choice(st); d = defs[n]; t = get_slot(d, slot); x = get(t, path)
    return {**defs, n: set_slot(d, slot, put(t, path, (x[0], x[2], x[1])))}


def erasub_apply(defs, rng):
    """Replace a closed (wire-balanced) subtree of size > 1 by an eraser: deletes computation that may be dead."""
    st = []
    for n, d in defs.items():
        for slot, t in stmts(d):
            for path, x in nodes(t):
                if path and x[0] in KIDS:
                    vc = var_counts(x, {}); dv = None
                    st.append((n, slot, path, x, vc))
    if not st: return None
    n, slot, path, x, vc = rng.choice(st); d = defs[n]
    t = put(get_slot(d, slot), path, ("era",)); d = set_slot(d, slot, t)
    # wires whose other end was inside the removed subtree are now dangling: erase them too
    rem = def_vars(d)
    for v, c in vc.items():
        if c == 1 and rem.get(v) == 1:
            for s2, t2 in list(stmts(d)):
                for p2, y in nodes(t2):
                    if y == ("var", v): d = set_slot(d, s2, put(get_slot(d, s2), p2, ("era",))); break
    r, rd, _ = reduce_def(*d)
    return {**defs, n: (r, rd)}


TARGETED = {
    "preset": (preset_sites, preset_apply),
    "litfirst": (litfirst_sites, litfirst_apply),
    "eqz": (eqz_sites, eqz_apply),
    "eqzi": (eqzi_sites, eqzi_apply),
    "numopr": (numopr_sites, numopr_apply),
    "duperase": (duperase_sites, duperase_apply),
    "inline_call": (call_sites, call_apply),
    "inline_leaf": (leaf_sites, leaf_apply),
}
RANDOM = {"rewire": rewire_apply, "cutwire": cutwire_apply, "opsym": opsym_apply, "lit": lit_apply,
          "swapkids": swapkids_apply, "erasub": erasub_apply}


def apply_all(defs, op):
    """Apply a targeted operator at every site, re-enumerating after each application (bounded)."""
    sites_f, apply_f = TARGETED[op]
    done = 0; seen_fail = set()
    for _ in range(200):
        st = [s for s in sites_f(defs) if repr(s) not in seen_fail]
        if not st: break
        s = st[0]; new = apply_f(defs, s)
        if new is None: seen_fail.add(repr(s)); continue
        defs = new; done += 1
    return defs, done
