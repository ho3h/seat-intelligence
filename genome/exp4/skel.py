"""Net <-> (skeleton, matching) converter for the factorized-generation test.

Skeleton: the book with every wire occurrence replaced by a blank slot `_` (same text format otherwise).
Matching: per definition, a list of slot-index pairs (indices count blanks in textual order within that definition:
root tree first, then each redex left side, then right side). Refill names wires w0, w1, ... per definition.
Round trip is exact modulo wire names (checked by canon()).
"""
from __future__ import annotations
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from genome.netast import parse_book, print_book, show

KIDS = ("con", "dup", "opr", "swi")


def _slots(t, acc):
    """Replace vars by ('var','_') and collect the names in textual order."""
    if t[0] == "var": acc.append(t[1]); return ("var", "_")
    if t[0] in KIDS: return (t[0], _slots(t[1], acc), _slots(t[2], acc))
    return t


def to_skeleton(defs, order):
    """Returns (skel_defs, matchings): skel_defs same shape as defs with blanks; matchings[name] = [(i, j), ...] i<j."""
    sk, match = {}, {}
    for n in order:
        root, reds = defs[n]; names = []
        r = _slots(root, names)
        rs = [(p, _slots(a, names), _slots(b, names)) for p, a, b in reds]
        pos = {}
        for i, v in enumerate(names): pos.setdefault(v, []).append(i)
        bad = [v for v, l in pos.items() if len(l) != 2]
        if bad: raise ValueError(f"@{n}: wires not used exactly twice: {bad[:5]}")
        sk[n] = (r, rs); match[n] = sorted(tuple(l) for l in pos.values())
    return sk, match


def n_slots(skdef):
    root, reds = skdef; acc = []
    _slots(root, acc)
    for _, a, b in reds: _slots(a, acc); _slots(b, acc)
    return len(acc)


def _fill(t, it):
    if t[0] == "var":
        x = next(it); return ("era",) if x == "*" else ("var", x)
    if t[0] in KIDS: return (t[0], _fill(t[1], it), _fill(t[2], it))
    return t


def refill(skdefs, order, matchings, erase_unmatched=False):
    """Put a matching back into a skeleton. matchings[name] = list of pairs covering all slots exactly once
    (with erase_unmatched, a slot left out of the matching becomes an eraser `*`)."""
    out = {}
    for n in order:
        root, reds = skdefs[n]; k = n_slots(skdefs[n])
        lab = [None] * k
        for w, (i, j) in enumerate(matchings[n]):
            assert lab[i] is None and lab[j] is None and i != j, (n, i, j)
            lab[i] = lab[j] = f"w{w}"
        if erase_unmatched: lab = [x if x is not None else "*" for x in lab]
        assert all(x is not None for x in lab), n
        it = iter(lab)
        out[n] = (_fill(root, it), [(p, _fill(a, it), _fill(b, it)) for p, a, b in reds])
    return out


def canon(defs, order):
    """Print with wires renamed by first occurrence per definition (alpha-normal form)."""
    out = {}
    for n in order:
        root, reds = defs[n]; names = []
        _slots(root, names)
        for _, a, b in reds: _slots(a, names); _slots(b, names)
        m = {}
        for v in names: m.setdefault(v, f"v{len(m)}")
        it = iter([m[v] for v in names])
        out[n] = (_fill(root, it), [(p, _fill(a, it), _fill(b, it)) for p, a, b in reds])
    return print_book(out, order)


def skeleton_text(skdefs, order):
    return print_book(skdefs, order)


def roundtrip_ok(text):
    defs, order = parse_book(text)
    sk, m = to_skeleton(defs, order)
    # also through text: print skeleton, reparse (blank `_` parses as a var named `_`)
    d2, o2 = parse_book(skeleton_text(sk, order))
    assert o2 == order
    back = refill(d2, order, m)
    return canon(back, order) == canon(defs, order), print_book(back, order)
