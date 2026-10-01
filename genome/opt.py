"""Net optimizer: semantics-preserving rewrites on verified nets, judged by the executor.

P1  static reduction: interactions inside a definition that cannot depend on runtime inputs are done once, ahead of time
    (constructor annihilation, eraser spreading, void pairs, number copying, wire substitution).
P2  inlining: a call `& @f ~ (args)` that always fires is replaced by f's body (only non-recursive, small, dup-safe defs).
Both are exact: a definition is instantiated fresh at every call and the physics is confluent. Nothing is trusted: every
optimized net is re-verified against the hidden suite before it is credited.
"""
from __future__ import annotations
import itertools
from .netast import parse_book, print_book, size

KIDS = ("con", "dup", "opr", "swi")
_fresh = itertools.count()


def var_counts(t, acc):
    if t[0] == "var": acc[t[1]] = acc.get(t[1], 0) + 1
    elif t[0] in KIDS: var_counts(t[1], acc); var_counts(t[2], acc)
    return acc


def subst(t, v, new):
    """Replace the (single) occurrence of var v in t by new."""
    if t[0] == "var": return new if t[1] == v else t
    if t[0] in KIDS: return (t[0], subst(t[1], v, new), subst(t[2], v, new))
    return t


def has(t, kind):
    if t[0] == kind: return True
    return t[0] in KIDS and (has(t[1], kind) or has(t[2], kind))


def refs_of(t, acc):
    if t[0] == "ref": acc.add(t[1])
    elif t[0] in KIDS: refs_of(t[1], acc); refs_of(t[2], acc)
    return acc


def reduce_def(root, reds):
    """P1 to a fixpoint. Returns (root, reds, n_removed_interactions_estimate)."""
    reds = list(reds); removed = 0
    changed = True
    while changed:
        changed = False
        counts = {}
        var_counts(root, counts)
        for _, a, b in reds: var_counts(a, counts); var_counts(b, counts)
        for i, (par, a, b) in enumerate(reds):
            # wire substitution: v ~ T with v having exactly one other occurrence
            for x, y in ((a, b), (b, a)):
                if x[0] == "var" and counts.get(x[1], 0) == 2 and not (y[0] == "var" and y[1] == x[1]):
                    v = x[1]
                    if v in var_counts(y, {}):  # x occurs in y: a cycle, leave it
                        continue
                    rest = reds[:i] + reds[i + 1:]
                    if v in var_counts(root, {}): root = subst(root, v, y)
                    else:
                        for j, (p2, a2, b2) in enumerate(rest):
                            if v in var_counts(a2, {}) or v in var_counts(b2, {}):
                                rest[j] = (p2, subst(a2, v, y), subst(b2, v, y)); break
                    reds = rest; changed = True; break
            if changed: break
            ka, kb = a[0], b[0]
            if ka in ("con", "dup", "opr", "swi") and ka == kb:                       # annihilation
                reds = reds[:i] + reds[i + 1:] + [(par, a[1], b[1]), (par, a[2], b[2])]; removed += 1; changed = True; break
            for x, y in ((a, b), (b, a)):
                if x[0] == "era" and y[0] in KIDS:                                    # eraser spreads
                    reds = reds[:i] + reds[i + 1:] + [(par, x, y[1]), (par, x, y[2])]; removed += 1; changed = True; break
                if x[0] == "num" and y[0] in ("con", "dup"):                          # number copies into both ports
                    reds = reds[:i] + reds[i + 1:] + [(par, x, y[1]), (par, x, y[2])]; removed += 1; changed = True; break
                if x[0] in ("era", "num", "ref") and y[0] in ("era", "num") and not (x[0] == "ref" and y[0] == "ref"):
                    if x[0] in ("era",) or y[0] in ("era",) or (x[0] == "num" and y[0] == "num") or (x[0] == "ref" and y[0] == "num") or (x[0] == "num" and y[0] == "ref"):
                        reds = reds[:i] + reds[i + 1:]; removed += 1; changed = True; break
            if changed: break
    return root, reds, removed


def call_graph(defs):
    return {n: refs_of(defs[n][0], set()) | set().union(*[refs_of(a, set()) | refs_of(b, set()) for _, a, b in defs[n][1]]) if defs[n][1] else refs_of(defs[n][0], set()) for n in defs}


def recursive(defs, cg):
    """names that can reach themselves"""
    rec = set()
    for n in defs:
        seen, stack = set(), list(cg[n])
        while stack:
            m = stack.pop()
            if m == n: rec.add(n); break
            if m in seen or m not in defs: continue
            seen.add(m); stack.extend(cg[m])
    return rec


def rename(t, suffix, keep=()):
    if t[0] == "var": return t if t[1] in keep else ("var", t[1] + suffix)
    if t[0] in KIDS: return (t[0], rename(t[1], suffix, keep), rename(t[2], suffix, keep))
    return t


def inline_pass(defs, order, max_size=40):
    cg = call_graph(defs); rec = recursive(defs, cg); n_inl = 0
    for dn in order:
        if dn == "main": continue
        root, reds = defs[dn]; new = []
        d_has_dup = has(root, "dup") or any(has(a, "dup") or has(b, "dup") for _, a, b in reds)
        for par, a, b in reds:
            for x, y in ((a, b), (b, a)):
                if x[0] == "ref" and x[1] in defs and x[1] != dn and x[1] not in rec and y[0] == "con":
                    froot, freds = defs[x[1]]
                    fsize = size(froot) + sum(size(p) + size(q) for _, p, q in freds)
                    f_dup = has(froot, "dup") or any(has(p, "dup") or has(q, "dup") for _, p, q in freds)
                    if fsize > max_size or (f_dup and not d_has_dup): continue
                    suf = f"_i{next(_fresh)}"
                    new.append((par, rename(froot, suf), y))
                    new.extend((p2, rename(p, suf), rename(q, suf)) for p2, p, q in freds)
                    n_inl += 1; break
            else:
                new.append((par, a, b)); continue
        r2, reds2, _ = reduce_def(root, new)
        defs[dn] = (r2, reds2)
    return n_inl


def optimize(book_text: str, inline: bool = True, rounds: int = 2, max_size: int = 40):
    defs, order = parse_book(book_text); stats = {"inlined": 0, "static": 0}
    for n in order:
        r, rd, k = reduce_def(*defs[n]); defs[n] = (r, rd); stats["static"] += k
    if inline:
        for _ in range(rounds):
            k = inline_pass(defs, order, max_size); stats["inlined"] += k
            if not k: break
    return print_book(defs, order), stats
