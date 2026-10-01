"""HERO-1 seating stage language, policy semantics, reference implementation and independent rule checker.

A stage program is one word per line (canonical order shown):

  size N                  capacity: at most N guests per section (1..6; default 6)
  together company        guests of one company are seated in one section (whole company or as few sections as it can fit)
  together <cat>          all guests of a category are seated together (same rule)
  limit <cat>+ K          at most K guests from the union of the listed categories per section (K >= 1)
  apart <catA> <catB>     no guest of catA shares a section with a guest of catB (catA != catB)
  order <cat>+            seat the listed categories first, in this order (lower section numbers)

Categories: ai_lab big_tech chips software_security investor government unlabelled  (data/hero/luncheon.json `category`).
Guests carry only `org` (printed company or None) and `category`; nothing else is ever read.

Semantics (the reference; genome/hero1/sectioner.py is the verified net of the same function):
  1. PREP (host): each guest belongs to a UNIT: all guests of category c if `together c`; else all guests of the same org
     if `together company` and org is not None; else the guest alone. Units are sorted by (rank(cat), index of the first
     member) with rank = position in `order` (unlisted = after all listed), members in index order. This is the guest
     SEQUENCE; element = (category, s) with s = unit size on the unit's first member, 0 on the others.
  2. SECTIONER (net): next-fit over the sequence. State: section number, size, per-rule counters (a, b).
     For a guest (c, s): t = max(s, 1). The guest fits the current section iff size + t <= cap and, for every rule (mA, mB, k)
     with inA = c in mA, inB = c in mB:  not ( (inA and (a + t > k or b > 0)) or (inB and a > 0) ).
     If it fits the section is kept, else a new section is opened (if the current one is non-empty). Then the guest is
     admitted: size += 1; a += inA; b += inB. Output: the section number of each guest.
     A `limit` word is the rule (mask, 0, K); an `apart` word is (maskA, maskB, INF).
  Sections are contiguous runs of the sequence, so they are contiguous runs of seats when the sequence is laid out on the table.
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import re
from dataclasses import dataclass, field

CATS = ["ai_lab", "big_tech", "chips", "software_security", "investor", "government", "unlabelled"]
CID = {c: i for i, c in enumerate(CATS)}
INF = (1 << 24) - 1
MAXCAP = 6


class ParseError(ValueError):
    pass


@dataclass
class Policy:
    cap: int = MAXCAP
    tog_company: bool = False
    tog_cats: tuple = ()                 # category ids, sorted
    limits: tuple = ()                   # ((cat ids sorted), k)
    aparts: tuple = ()                   # ((catA, catB) with A < B)
    order: tuple = ()                    # category ids in priority order

    def canon(self):
        return Policy(self.cap, self.tog_company, tuple(sorted(set(self.tog_cats))),
                      tuple(sorted((tuple(sorted(set(c))), k) for c, k in self.limits)),
                      tuple(sorted(set(tuple(sorted(p)) for p in self.aparts))), tuple(self.order))

    def rules(self):
        """the net's rule table: [(maskA, maskB, k)]"""
        out = []
        for cs, k in self.limits: out.append((sum(1 << c for c in cs), 0, k))
        for a, b in self.aparts: out.append((1 << a, 1 << b, INF))
        return out

    def sig(self):
        s = set()
        if self.cap != MAXCAP: s.add("size")
        if self.tog_company: s.add("tc")
        if self.tog_cats: s.add("tk")
        if self.limits: s.add("lim")
        if self.aparts: s.add("apt")
        if self.order: s.add("ord")
        return frozenset(s)


def to_text(pol):
    p = pol.canon(); L = []
    if p.cap != MAXCAP: L.append(f"size {p.cap}")
    if p.tog_company: L.append("together company")
    for c in p.tog_cats: L.append(f"together {CATS[c]}")
    for cs, k in p.limits: L.append("limit " + " ".join(CATS[c] for c in cs) + f" {k}")
    for a, b in p.aparts: L.append(f"apart {CATS[a]} {CATS[b]}")
    if p.order: L.append("order " + " ".join(CATS[c] for c in p.order))
    return "\n".join(L) if L else "none"


def parse(text):
    """-> Policy. Strict: raises ParseError on anything not in the vocabulary. Tolerates code fences and blank lines."""
    lines = [l.strip() for l in text.strip().splitlines()]
    lines = [l for l in lines if l and not l.startswith("```")]
    if lines == ["none"] or not lines: return Policy()
    cap, tc, tk, lim, apt, order = None, False, [], [], [], None
    for l in lines:
        t = l.split(); w = t[0]
        if w == "size" and len(t) == 2 and t[1].isdigit():
            if cap is not None: raise ParseError("size twice")
            cap = int(t[1])
            if not 1 <= cap <= MAXCAP: raise ParseError(f"size out of range: {l}")
        elif w == "together" and len(t) == 2:
            if t[1] == "company": tc = True
            elif t[1] in CID: tk.append(CID[t[1]])
            else: raise ParseError(f"bad together: {l}")
        elif w == "limit" and len(t) >= 3 and t[-1].isdigit() and all(x in CID for x in t[1:-1]):
            k = int(t[-1])
            if not 1 <= k <= 6: raise ParseError(f"limit out of range: {l}")
            lim.append((tuple(CID[x] for x in t[1:-1]), k))
        elif w == "apart" and len(t) == 3 and t[1] in CID and t[2] in CID and t[1] != t[2]:
            apt.append((CID[t[1]], CID[t[2]]))
        elif w == "order" and len(t) >= 2 and all(x in CID for x in t[1:]):
            if order is not None: raise ParseError("order twice")
            ids = [CID[x] for x in t[1:]]
            if len(set(ids)) != len(ids): raise ParseError("repeated category in order")
            order = ids
        else: raise ParseError(f"unknown word: {l}")
    return Policy(cap if cap is not None else MAXCAP, tc, tuple(tk), tuple(lim), tuple(apt), tuple(order or ())).canon()


# ------------------------------------------------------------------ guests
# a guest is (org or None, category id). Real luncheon: data/hero/luncheon.json.
def load_real(path=_REPO + "/data/hero/luncheon.json"):
    import json
    d = json.load(open(path))
    seats = d["seats"]
    return [(s["org"], CID[s["category"]]) for s in seats], seats


def prep(guests, pol):
    """-> sequence [(guest index, cat, s)] (see module doc)."""
    n = len(guests)
    tk = set(pol.tog_cats)
    rank = {c: i for i, c in enumerate(pol.order)}; R = len(pol.order)
    unit_of, members = [None] * n, {}
    for i, (org, c) in enumerate(guests):
        if c in tk: key = ("c", c)
        elif pol.tog_company and org is not None: key = ("o", org)
        else: key = ("g", i)
        unit_of[i] = key; members.setdefault(key, []).append(i)
    units = []
    for key, ms in members.items():
        cats = {guests[i][1] for i in ms}
        assert len(cats) == 1, ("company with two categories", key)
        c = guests[ms[0]][1]
        units.append((rank.get(c, R), ms[0], ms, c))
    units.sort(key=lambda u: (u[0], u[1]))
    seq = []
    for _, _, ms, c in units:
        for j, i in enumerate(ms): seq.append((i, c, len(ms) if j == 0 else 0))
    return seq


def ref_sections(cap, rules, elems):
    """Reference of the net: elems [(cat, s)] -> [section number]. Exactly the function in the module doc."""
    S = [[a, b, k, 0, 0] for a, b, k in rules]
    sec = size = 0; out = []
    for c, s in elems:
        t = s if s > 0 else 1
        ok = size + t <= cap
        ins = [(a >> c) & 1 for a, b, k, _, _ in S]; inb = [(r[1] >> c) & 1 for r in S]
        for r, ia, ib in zip(S, ins, inb):
            if (ia and (r[3] + t > r[2] or r[4] > 0)) or (ib and r[3] > 0): ok = False
        if not ok:
            if size > 0: sec += 1
            size = 0
            for r in S: r[3] = r[4] = 0
        for r, ia, ib in zip(S, ins, inb): r[3] += ia; r[4] += ib
        size += 1
        out.append(sec)
    return out


def assign_ref(guests, pol):
    """per-guest section number (Python reference of the whole pipeline)."""
    seq = prep(guests, pol)
    secs = ref_sections(pol.cap, pol.rules(), [(c, s) for _, c, s in seq])
    a = [None] * len(guests)
    for (i, _, _), sc in zip(seq, secs): a[i] = sc
    return a


def seat_order(guests, pol):
    """guest indices in seating sequence order (position p = p-th seat along the table)."""
    return [i for i, _, _ in prep(guests, pol)]


# ------------------------------------------------------------------ independent rule checker (does not use next-fit)
def max_fit(pol, c):
    m = pol.cap
    for cs, k in pol.limits:
        if c in cs: m = min(m, k)
    return m


def violations(guests, pol, assign):
    """Rule violations of an arbitrary assignment guest -> section id (any hashable). Counts:
       cap:      sum over sections of max(0, size - cap)
       limit:    sum over sections and limit rules of max(0, #guests in the listed categories - k)
       apart:    number of (guest in A, guest in B) pairs sharing a section
       together: for each unit that `together` asks for: (#sections it spans) - ceil(size / max_fit(category)), if positive
       order:    number of (g, h) pairs with rank(g) < rank(h) and section(h) < section(g)   (sections compared as numbers)
    """
    p = pol.canon(); n = len(guests)
    secs = {}
    for i, s in enumerate(assign): secs.setdefault(s, []).append(i)
    v = dict(cap=0, limit=0, apart=0, together=0, order=0)
    for s, ms in secs.items():
        v["cap"] += max(0, len(ms) - p.cap)
        cc = {}
        for i in ms: cc[guests[i][1]] = cc.get(guests[i][1], 0) + 1
        for cs, k in p.limits: v["limit"] += max(0, sum(cc.get(c, 0) for c in cs) - k)
        for a, b in p.aparts: v["apart"] += cc.get(a, 0) * cc.get(b, 0)
    units = {}
    tk = set(p.tog_cats)
    for i, (org, c) in enumerate(guests):
        if c in tk: units.setdefault(("c", c), []).append(i)
        elif p.tog_company and org is not None: units.setdefault(("o", org), []).append(i)
    for key, ms in units.items():
        c = guests[ms[0]][1]; mf = max_fit(p, c)
        spans = len({assign[i] for i in ms}); need = -(-len(ms) // mf)
        v["together"] += max(0, spans - need)
    if p.order:
        rank = {c: i for i, c in enumerate(p.order)}; R = len(p.order)
        rk = [rank.get(guests[i][1], R) for i in range(n)]
        for g in range(n):
            for h in range(n):
                if rk[g] < rk[h] and assign[h] < assign[g]: v["order"] += 1
    v["total"] = sum(v.values())
    return v


def violations_fast(guests, pol, assign):
    """same as violations() without the O(n^2) order term (order is monotone by construction for the pipeline; the scale test
    checks it separately in O(n log n))."""
    p = pol.canon(); q = Policy(p.cap, p.tog_company, p.tog_cats, p.limits, p.aparts, ())
    return violations(guests, q, assign)


def order_inversions_fast(guests, pol, assign):
    """O(n log n) count of the order term: pairs (g,h), rank g < rank h, section h < section g."""
    p = pol.canon()
    if not p.order: return 0
    rank = {c: i for i, c in enumerate(p.order)}; R = len(p.order)
    import bisect
    by = {}
    for i, (_, c) in enumerate(guests): by.setdefault(rank.get(c, R), []).append(assign[i])
    tot = 0; seen = []                         # sections of all guests with smaller rank, sorted
    for r in sorted(by):
        for s in by[r]:
            # guests g of smaller rank with section(g) > s  are inversions with h at section s
            tot += len(seen) - bisect.bisect_right(seen, s)
        for s in by[r]: bisect.insort(seen, s)
    return tot


def posted_assignment(n, cap=MAXCAP):
    """The posted chart as sections: seats walked around the table (left row 0..16 then right row 16..0), cut into
    consecutive blocks of `cap` seats. Guest index i = position in luncheon.json (left 0..16, right 0..16)."""
    half = n // 2
    walk = list(range(half)) + [half + r for r in range(half - 1, -1, -1)] + list(range(2 * half, n))
    a = [None] * n
    for p, gi in enumerate(walk): a[gi] = p // cap
    return a
