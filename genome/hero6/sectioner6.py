"""HERO-6 verified kernel: the HERO-1 sectioner with tag bitmasks, so the named word `avoid` is a checked rule.

Input (cap, rules, guests): cap u24; rules = list of (maskA, maskB, k); guests = list of (T, M, s).
  T = test tags, M = own tags (bit c for the guest's category, bits 7.. for the avoid names it matches; T = M except on
  a unit's first element, where T also carries the named bits of the whole unit: the unit look-ahead of seating.js).
  A rule tests (mask & T) != 0 for the fit check and counts (mask & M) != 0 on admission.
Output: list of section numbers. Reference: genome/hero6/lang6.py `ref_tags` (equal to the JS/Python seating reference
`ref_sections6` on every policy, genome/hero6/selftest6.py). With T = M = 1 << category this is exactly the HERO-1 net's
function (a `limit` is (mask, 0, K), an `apart` (maskA, maskB, INF), an `avoid X Y` (bitX, bitY, INF)).

Differences from genome/hero1/sectioner.py (frozen, unchanged): the guest is (T (M s)) instead of (c s); the walker `st`
takes T and M instead of c; inA/inB for the check = (mask & T) > 0 instead of (mask >> c) & 1; the admission increments
use (mask & M) > 0.
"""
from __future__ import annotations
import os, sys, random, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genome.types import tup, u24, list_of

RULE = tup(u24, u24, u24)
GUEST = tup(u24, u24, u24)
INP = tup(u24, list_of(RULE), list_of(GUEST))
OUT = list_of(u24)
INF = (1 << 24) - 1

NET = r"""
@prog = ((cap (rules gs)) out)
  & @init ~ (rules S)
  & @go ~ (gs (cap (0 (0 (S out)))))

@init = ((?((@in_nil @in_cons) (p out)) p) out)

@in_nil = (* (0 *))

@in_cons = (* (((mA (mB k)) t) (1 ((mA (mB (k (0 0)))) t2))))
  & @init ~ (t t2)

@go = ((?((@go_nil @go_cons) (p (cap (sec (size (S out)))))) p) (cap (sec (size (S out)))))

@go_nil = (* (* (* (* (* (0 *))))))

@go_cons = (* (((T (M s)) tl) (cap (sec (size (S out))))))
  & cap ~ {cap1 cap2}
  & s ~ {s1 s2}
  & s1 ~ $([=] $(0 z))
  & s2 ~ $([+] $(z t))
  & t ~ {t1 t2}
  & size ~ {sz1 sz2}
  & sz1 ~ $([+] $(t2 x))
  & x ~ $([>] $(cap1 g))
  & g ~ $([^] $(1 okc))
  & @st ~ (S (T (M (t1 (1 (ok (S1 S2)))))))
  & ok ~ $([&] $(okc okk))
  & okk ~ ?((@fresh @keep) (sec (sz2 (S1 (S2 (cap2 (tl out)))))))

@keep = (* (sec (size (S1 (S2 (cap (tl (1 (sec1 tout)))))))))
  & S2 ~ *
  & sec ~ {sec1 sec2}
  & size ~ $([+1] size2)
  & @go ~ (tl (cap (sec2 (size2 (S1 tout)))))

@fresh = (sec (size (S1 (S2 (cap (tl (1 (sec1 tout))))))))
  & S1 ~ *
  & size ~ ?((@sec_same @sec_bump) (sec s3))
  & s3 ~ {sec1 sec2}
  & @go ~ (tl (cap (sec2 (1 (S2 tout)))))

@sec_same = (a a)

@sec_bump = (* (a s))
  & a ~ $([+1] s)

@st = ((?((@st_nil @st_cons) (p (T (M (t (acc out)))))) p) (T (M (t (acc out)))))

@st_nil = (* (* (* (* (acc (acc ((0 *) (0 *))))))))

@st_cons = (* (((mA (mB (k (a b)))) tl) (T (M (t (acc (okf ((1 ((mA2 (mB2 (k2 (na nb)))) tl1)) (1 ((mA3 (mB3 (k3 (ia3 ib3)))) tl2))))))))))
  & mA ~ {mA1 {mA2 {mA3 mA4}}}
  & mB ~ {mB1 {mB2 {mB3 mB4}}}
  & T ~ {Ta {Tb Tc}}
  & M ~ {Ma {Mb Mc}}
  & k ~ {k1 {k2 k3}}
  & a ~ {a1 {a2 a3}}
  & b ~ {b1 b2}
  & t ~ {t1 t2}
  & mA1 ~ $([&] $(Ta x1))
  & x1 ~ $([>] $(0 ia1))
  & mB1 ~ $([&] $(Tb x2))
  & x2 ~ $([>] $(0 ib1))
  & mA4 ~ $([&] $(Ma y1))
  & y1 ~ $([>] $(0 jA))
  & mB4 ~ $([&] $(Mb y2))
  & y2 ~ $([>] $(0 jB))
  & jA ~ {ia2 ia3}
  & jB ~ {ib2 ib3}
  & a1 ~ $([+] $(t1 at))
  & at ~ $([>] $(k1 gt))
  & b1 ~ $([>] $(0 bp))
  & gt ~ $([|] $(bp v1))
  & ia1 ~ $([&] $(v1 v1a))
  & a2 ~ $([>] $(0 ap))
  & ib1 ~ $([&] $(ap v2))
  & v1a ~ $([|] $(v2 viol))
  & viol ~ $([^] $(1 okr))
  & acc ~ $([&] $(okr acc2))
  & a3 ~ $([+] $(ia2 na))
  & b2 ~ $([+] $(ib2 nb))
  & @st ~ (tl (Tc (Mc (t2 (acc2 (okf (tl1 tl2)))))))
"""


def net_text():
    return NET.strip() + "\n"


def _ref(x):
    from genome.hero6.lang6 import ref_tags
    cap, rules, guests = x
    return ref_tags(cap, [tuple(r) for r in rules], [tuple(g) for g in guests])


def _gen_runs(r, n, nnames):
    """units of one category; each member may carry named bits; T of a unit's first element = OR of the unit's named bits."""
    out = []
    raw = r.random() < 0.2
    w = [r.random() ** 2 + 0.02 for _ in range(7)]
    def own(c):
        m = 1 << c
        for j in range(nnames):
            if r.random() < 0.25: m |= 1 << (7 + j)
        return m
    while len(out) < n:
        c = r.choices(range(7), w)[0]
        if raw:
            M = own(c); T = M | (r.randrange(1 << 24) & ~0x7F & ((1 << (7 + nnames)) - 1) if r.random() < 0.3 else 0)
            out.append((T, M, r.choice([0, 0, 1, 1, 2, 3, 5, 8]))); continue
        s = r.choice([1, 1, 1, 1, 2, 2, 3, 4, 5, 7, 9])
        ms = [own(c) for _ in range(s)]
        U = 0
        for m in ms: U |= m & ~0x7F
        out += [(ms[0] | U, ms[0], s)] + [(m, m, 0) for m in ms[1:]]
    return out[:n] if r.random() < 0.5 else out


def _gen(r, n):
    cap = r.choice([1, 2, 3, 4, 5, 6, 6, 6, 8, 100])
    nnames = r.choice([0, 1, 2, 3, 4, 6, 17])
    rules = []
    for _ in range(r.choice([0, 1, 1, 2, 2, 3, 4, 5])):
        u = r.random()
        if u < 0.35:
            m = 0
            while m == 0: m = sum(1 << c for c in range(7) if r.random() < 0.35)
            rules.append((m, 0, r.choice([1, 1, 2, 2, 3, 6])))
        elif u < 0.6 or nnames < 2:
            cs = r.sample(range(7), 2)
            rules.append((1 << cs[0], 1 << cs[1], INF))
        else:
            a, b = r.sample(range(nnames), 2)
            rules.append((1 << (7 + a), 1 << (7 + b), INF))
    return (cap, rules, _gen_runs(r, n, nnames))


B7, B8, B9 = 1 << 7, 1 << 8, 1 << 9
EDGES = [
    (6, [], []), (6, [], [(1, 1, 1)]), (1, [], [(1, 1, 1), (2, 2, 1), (4, 4, 0)]),
    (6, [(1, 0, 1)], [(1, 1, 1), (1, 1, 1), (2, 2, 1)]),                                  # HERO-1 limit, tags = 1 << c
    (6, [(1, 2, INF)], [(1, 1, 1), (2, 2, 1), (1, 1, 1), (2, 2, 1)]),                     # HERO-1 apart
    (6, [(B7, B8, INF)], [(1 | B7, 1 | B7, 1), (2 | B8, 2 | B8, 1), (4, 4, 1)]),         # avoid X Y: Y opens a new section
    (6, [(B7, B8, INF)], [(4, 4, 1), (8 | B7 | B8, 8 | B7, 2), (8 | B8, 8 | B8, 0)]),     # unit holding X and Y: forced together
    (6, [(B7, B8, INF)], [(2 | B8, 2 | B8, 1), (1 | B7, 1, 3), (1, 1, 0), (1 | B7, 1 | B7, 0)]),  # look-ahead: unit with an X later
    (6, [(B7, B8, INF)], [(1 | B7 | B8, 1 | B7 | B8, 1), (2, 2, 1), (4 | B7, 4 | B7, 1)]),  # one guest matches both
    (3, [(B7, B9, INF), (32, 0, 1)], [(32 | B9, 32 | B9, 1), (32, 32, 1), (1 | B7, 1 | B7, 1), (64 | B9, 64 | B9, 1)]),
    (6, [(127, 0, 6)], [(1 << c, 1 << c, 1) for c in range(7)] * 3),
    (6, [(1 << 23, 1 << 22, INF)], [(1 | (1 << 23), 1 | (1 << 23), 1), (2 | (1 << 22), 2 | (1 << 22), 1)]),  # top tag bits
    (6, [], [(1, 1, 0), (1, 1, 0), (2, 2, 0)]),
]

SIZES = [4, 8, 16, 32]
TEST_SIZES = [128, 320]


def make_program():
    from genome.corpus import REGISTRY, program
    pid = "hero6_sectioner_tags"
    if pid in REGISTRY: return REGISTRY[pid]
    return program(pid, "T5", "HERO-6 sectioner: next-fit seating into sections with rule counters over guest tag bitmasks (genome/hero6/lang6.py ref_tags).",
                   INP, OUT, _ref, _gen, SIZES, TEST_SIZES, edges=list(EDGES))


def verify_kernel(seeds=(0, 1, 2), workers=6, timeout=60.0):
    from genome.verify import verify
    p = make_program(); res = []
    for s in seeds:
        t = time.time()
        r = verify(p, net_text(), s, timeout, workers=workers)
        r["seed"] = s; r["secs"] = round(time.time() - t, 1); res.append(r)
        print("seed", s, r["status"], r.get("cases"), r.get("failed"), r.get("metrics"), r.get("counterexample") or r.get("reason") or "", r["secs"], "s", flush=True)
    return res


if __name__ == "__main__":
    print(net_text()) if len(sys.argv) > 1 and sys.argv[1] == "net" else verify_kernel(tuple(int(a) for a in sys.argv[1:]) or (0, 1, 2))
