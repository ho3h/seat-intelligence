"""HERO-6 seating language: the six HERO-1 words (behaviour unchanged, imported from genome/hero1/lang.py) plus two words
over NAMED guests or companies.

  avoid X Y     no guest matching X shares a section with a guest matching Y (X != Y)
  pair X Y      the guests matching X and the guests matching Y sit in one section (X != Y)

X and Y are single tokens: a guest's name or a printed company with every run of spaces/commas written as `_`
(key(): "Elon Musk" -> Elon_Musk, "X, Tesla, Space X" -> X_Tesla_Space_X). A guest matches X iff key(name) == X or
key(org) == X. This is exactly `isWho` in demo/luncheon/seating.js.

Guests are (org, category id) or (org, category id, name). The old words never read the name.

Semantics (reference; must equal demo/luncheon/seating.js line for line):
  PREP: the HERO-1 units (together category / together company / single guest), sorted by (rank(cat), first index).
     `pair` (host side): union-find over units; for every pair word, every unit holding a guest matching X or Y is merged
     into one unit (a word that matches only one unit, or none, changes nothing). The merged unit takes the smallest
     (rank, first index) key of its parts (it sits at the earlier unit's position); its members are its parts in key
     order, each part's members in index order. Sequence element = (guest, OWN category, s) with s = unit size on the
     unit's first member and 0 on the others. Without `pair` this is exactly HERO-1 prep.
  SECTIONS: HERO-1 next-fit (cap, limit/apart rule counters), plus one flag pair (hasX, hasY) per avoid word.
     An element is blocked by `avoid X Y` if [any member of its unit (first element: the whole unit; other elements:
     itself) matches X and the section has a Y] or [... matches Y and the section has an X]. Flags reset on a new section;
     after admission the flags are set from the admitted guest only. Without `avoid` this is exactly HERO-1 ref_sections.
  CHECKER (independent of next-fit): HERO-1 counts + avoid = pairs (x, y), x matches X, y matches Y, x != y, same section;
     pair = pairs (x, y), x matches X, y matches Y, x != y, different sections.
Canonical text: the HERO-1 lines, then `avoid` lines, then `pair` lines; each named pair written with the smaller token
first (both words are symmetric), sorted, duplicates removed.
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import re
from dataclasses import dataclass
from genome.hero1 import lang as L1
from genome.hero1.lang import CATS, CID, INF, MAXCAP, ParseError, posted_assignment, max_fit  # noqa: F401

_SEP = re.compile(r"[\s,]+")


def key(x):
    return "" if x is None else _SEP.sub("_", str(x))


def name_of(g):
    return g[2] if len(g) > 2 else None


def is_who(g, who):
    return key(name_of(g)) == who or key(g[0]) == who


@dataclass
class Policy6:
    cap: int = MAXCAP
    tog_company: bool = False
    tog_cats: tuple = ()
    limits: tuple = ()
    aparts: tuple = ()
    order: tuple = ()
    avoids: tuple = ()          # ((X, Y) with X < Y)
    pairs: tuple = ()           # ((X, Y) with X < Y)

    def old(self):
        return L1.Policy(self.cap, self.tog_company, self.tog_cats, self.limits, self.aparts, self.order)

    def canon(self):
        o = self.old().canon()
        nm = lambda ps: tuple(sorted(set((min(a, b), max(a, b)) for a, b in ps)))
        return Policy6(o.cap, o.tog_company, o.tog_cats, o.limits, o.aparts, o.order, nm(self.avoids), nm(self.pairs))

    def rules(self):
        return self.old().rules()

    def sig(self):
        s = set(self.old().sig())
        if self.avoids: s.add("avd")
        if self.pairs: s.add("par")
        return frozenset(s)


def to_text(pol):
    p = pol.canon() if isinstance(pol, Policy6) else Policy6(*pol.canon().__dict__.values())
    base = L1.to_text(p.old())
    lines = [] if base == "none" else base.split("\n")
    lines += [f"avoid {a} {b}" for a, b in p.avoids] + [f"pair {a} {b}" for a, b in p.pairs]
    return "\n".join(lines) if lines else "none"


def parse(text):
    """strict; the old words go through HERO-1 parse unchanged."""
    lines = [l.strip() for l in text.strip().splitlines()]
    lines = [l for l in lines if l and not l.startswith("```")]
    old, avd, par = [], [], []
    for l in lines:
        t = l.split()
        if t[0] == "avoid" and len(t) == 3 and t[1] != t[2]: avd.append((t[1], t[2]))
        elif t[0] == "pair" and len(t) == 3 and t[1] != t[2]: par.append((t[1], t[2]))
        elif t[0] in ("avoid", "pair"): raise ParseError(f"bad {t[0]}: {l}")
        else: old.append(l)
    if (avd or par) and old == ["none"]: raise ParseError("none mixed with rules")
    o = L1.parse("\n".join(old)) if old else L1.Policy()
    return Policy6(o.cap, o.tog_company, o.tog_cats, o.limits, o.aparts, o.order, tuple(avd), tuple(par)).canon()


def load_real(path=_REPO + "/data/hero/luncheon.json"):
    import json
    seats = json.load(open(path))["seats"]
    return [(s["org"], CID[s["category"]], s["name"]) for s in seats], seats


# ------------------------------------------------------------------ reference
def prep(guests, pol):
    """-> sequence [(guest index, own category, s)]."""
    n = len(guests)
    tk = set(pol.tog_cats)
    rank = {c: i for i, c in enumerate(pol.order)}; R = len(pol.order)
    members = {}
    for i, g in enumerate(guests):
        org, c = g[0], g[1]
        if c in tk: k = ("c", c)
        elif pol.tog_company and org is not None: k = ("o", org)
        else: k = ("g", i)
        members.setdefault(k, []).append(i)
    units = []
    for k, ms in members.items():
        cats = {guests[i][1] for i in ms}
        assert len(cats) == 1, ("company with two categories", k)
        units.append(((rank.get(guests[ms[0]][1], R), ms[0]), ms))
    units.sort(key=lambda u: u[0])
    pairs = getattr(pol, "pairs", ())
    if pairs:
        par = list(range(len(units)))
        def find(x):
            while par[x] != x: par[x] = par[par[x]]; x = par[x]
            return x
        for X, Y in pairs:
            hit = [u for u, (_, ms) in enumerate(units) if any(is_who(guests[i], X) or is_who(guests[i], Y) for i in ms)]
            for u in hit[1:]:
                a, b = find(hit[0]), find(u)
                if a != b: par[max(a, b)] = min(a, b)      # root = the unit with the smallest key (units are sorted)
        groups = {}
        for u in range(len(units)): groups.setdefault(find(u), []).append(u)
        units = [(units[root][0], [i for u in us for i in units[u][1]]) for root, us in sorted(groups.items())]
    seq = []
    for _, ms in units:
        for j, i in enumerate(ms): seq.append((i, guests[i][1], len(ms) if j == 0 else 0))
    return seq


def ref_sections6(cap, rules, seq, guests, avoids):
    """next-fit with HERO-1 rule counters plus avoid flags (seating.js avoidSections)."""
    S = [[a, b, k, 0, 0] for a, b, k in rules]
    A = [[False, False] for _ in avoids]
    sec = size = 0; out = []
    for idx, (gi, c, s) in enumerate(seq):
        t = s if s > 0 else 1
        ok = size + t <= cap
        ia = [(r[0] >> c) & 1 for r in S]; ib = [(r[1] >> c) & 1 for r in S]
        for r, x, y in zip(S, ia, ib):
            if (x and (r[3] + t > r[2] or r[4] > 0)) or (y and r[3] > 0): ok = False
        mem = [guests[e[0]] for e in seq[idx: idx + s]] if s > 0 else [guests[gi]]
        for (X, Y), f in zip(avoids, A):
            ua = any(is_who(g, X) for g in mem); ub = any(is_who(g, Y) for g in mem)
            if (ua and f[1]) or (ub and f[0]): ok = False
        if not ok:
            if size > 0: sec += 1
            size = 0
            for r in S: r[3] = r[4] = 0
            for f in A: f[0] = f[1] = False
        for r, x, y in zip(S, ia, ib): r[3] += x; r[4] += y
        for (X, Y), f in zip(avoids, A):
            if is_who(guests[gi], X): f[0] = True
            if is_who(guests[gi], Y): f[1] = True
        size += 1
        out.append(sec)
    return out


def assign_ref(guests, pol):
    seq = prep(guests, pol)
    secs = ref_sections6(pol.cap, pol.rules(), seq, guests, list(getattr(pol, "avoids", ())))
    a = [None] * len(guests)
    for (i, _, _), sc in zip(seq, secs): a[i] = sc
    return a


def seat_order(guests, pol):
    return [i for i, _, _ in prep(guests, pol)]


# ------------------------------------------------------------------ checker
def violations(guests, pol, assign):
    p = pol.canon()
    g2 = [(g[0], g[1]) for g in guests]
    v = L1.violations(g2, p.old(), assign)
    tot = v.pop("total")
    v["avoid"] = v["pair"] = 0
    n = len(guests)
    def cross(X, Y, same):
        xs = [i for i in range(n) if is_who(guests[i], X)]; ys = [j for j in range(n) if is_who(guests[j], Y)]
        return sum(1 for i in xs for j in ys if i != j and (assign[i] == assign[j]) == same)
    for X, Y in p.avoids: v["avoid"] += cross(X, Y, True)
    for X, Y in p.pairs: v["pair"] += cross(X, Y, False)
    v["total"] = tot + v["avoid"] + v["pair"]
    return v


# ------------------------------------------------------------------ net input (tag bitmasks; genome/hero6/sectioner6.py)
NAMEBITS = 24 - 7          # u24 masks: 7 category bits + at most 17 named tags


def tag_input(guests, pol):
    """-> ((cap, rules, [(T, M, s)]), seq). M = own tags (category bit | bits of the avoid names the guest matches);
    T = test tags = M, except on a unit's first element where the named bits are OR-ed over the whole unit.
    Rules: HERO-1 rules (category masks) + one (bitX, bitY, INF) per avoid word."""
    p = pol.canon()
    names = sorted({x for ab in p.avoids for x in ab})
    if len(names) > NAMEBITS: raise ParseError(f"more than {NAMEBITS} distinct names in avoid words")
    bit = {nm: 1 << (7 + i) for i, nm in enumerate(names)}
    seq = prep(guests, p)
    own = {}
    for i, c, s in seq:
        m = 1 << c
        for nm, b in bit.items():
            if is_who(guests[i], nm): m |= b
        own[i] = m
    elems = []
    for idx, (i, c, s) in enumerate(seq):
        T = own[i]
        if s > 0:
            for e in seq[idx: idx + s]: T |= own[e[0]] & ~0x7F
        elems.append((T, own[i], s))
    rules = [tuple(r) for r in p.rules()] + [(bit[a], bit[b], INF) for a, b in p.avoids]
    return (p.cap, rules, elems), seq


def ref_tags(cap, rules, elems):
    """the function the tag net computes (reference of genome/hero6/sectioner6.py)."""
    S = [[a, b, k, 0, 0] for a, b, k in rules]
    sec = size = 0; out = []
    for T, M, s in elems:
        t = s if s > 0 else 1
        ok = size + t <= cap
        for r in S:
            x = (r[0] & T) != 0; y = (r[1] & T) != 0
            if (x and (r[3] + t > r[2] or r[4] > 0)) or (y and r[3] > 0): ok = False
        if not ok:
            if size > 0: sec += 1
            size = 0
            for r in S: r[3] = r[4] = 0
        for r in S: r[3] += (r[0] & M) != 0; r[4] += (r[1] & M) != 0
        size += 1
        out.append(sec)
    return out
