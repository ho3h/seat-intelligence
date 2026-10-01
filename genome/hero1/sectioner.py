"""HERO-1 verified kernel: the sectioner net (next-fit with rule counters), its corpus-style Program, and the hidden-suite runner.

Input  (cap, rules, guests): cap u24; rules = list of (maskA, maskB, k); guests = list of (category, s).
Output list of section numbers, one per guest.  Semantics: genome/hero1/lang.py `ref_sections` (see its module doc).

State list S has one cell per rule: (mA (mB (k (a b)))). One walker (`st`) rebuilds S twice at once (S1 = admit into the
current section, S2 = open a new section then admit) and computes the fit flag; the step then keeps one and erases the other.
"""
from __future__ import annotations
import os, sys, random, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genome.corpus import Program
from genome.types import tup, u24, list_of

RULE = tup(u24, u24, u24)
GUEST = tup(u24, u24)
INP = tup(u24, list_of(RULE), list_of(GUEST))
OUT = list_of(u24)

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

@go_cons = (* (((c s) tl) (cap (sec (size (S out))))))
  & cap ~ {cap1 cap2}
  & s ~ {s1 s2}
  & s1 ~ $([=] $(0 z))
  & s2 ~ $([+] $(z t))
  & t ~ {t1 t2}
  & size ~ {sz1 sz2}
  & sz1 ~ $([+] $(t2 x))
  & x ~ $([>] $(cap1 g))
  & g ~ $([^] $(1 okc))
  & @st ~ (S (c (t1 (1 (ok (S1 S2))))))
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

@st = ((?((@st_nil @st_cons) (p (c (t (acc out))))) p) (c (t (acc out))))

@st_nil = (* (* (* (acc (acc ((0 *) (0 *)))))))

@st_cons = (* (((mA (mB (k (a b)))) tl) (c (t (acc (okf ((1 ((mA2 (mB2 (k2 (na nb)))) tl1)) (1 ((mA3 (mB3 (k3 (ia3 ib3)))) tl2)))))))))
  & mA ~ {mA1 {mA2 mA3}}
  & mB ~ {mB1 {mB2 mB3}}
  & c ~ {ca {cb cc}}
  & k ~ {k1 {k2 k3}}
  & a ~ {a1 {a2 a3}}
  & b ~ {b1 b2}
  & t ~ {t1 t2}
  & mA1 ~ $([>>] $(ca x1))
  & x1 ~ $([&] $(1 inA))
  & mB1 ~ $([>>] $(cb x2))
  & x2 ~ $([&] $(1 inB))
  & inA ~ {ia1 {ia2 ia3}}
  & inB ~ {ib1 {ib2 ib3}}
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
  & @st ~ (tl (cc (t2 (acc2 (okf (tl1 tl2))))))
"""


def net_text():
    return NET.strip() + "\n"


# ---------------------------------------------------------------- Program (corpus contract) for genome.verify
def _ref(x):
    from genome.hero1.lang import ref_sections
    cap, rules, guests = x
    return ref_sections(cap, [tuple(r) for r in rules], [tuple(g) for g in guests])


def _gen_runs(r, n, ncat=7):
    """a guest sequence of about n guests built from runs (consistent units), sometimes raw random (c, s) pairs."""
    out = []
    raw = r.random() < 0.25
    w = [r.random() ** 2 + 0.02 for _ in range(ncat)]
    while len(out) < n:
        c = r.choices(range(ncat), w)[0]
        if raw: out.append((c, r.choice([0, 0, 1, 1, 2, 3, 5, 8]))); continue
        s = r.choice([1, 1, 1, 1, 2, 2, 3, 4, 5, 7, 9])
        out += [(c, s)] + [(c, 0)] * (s - 1)
    return out[:n] if r.random() < 0.5 else out


def _gen(r, n):
    cap = r.choice([1, 2, 3, 4, 5, 6, 6, 6, 8, 100])
    rules = []
    for _ in range(r.choice([0, 1, 1, 2, 2, 3, 4])):
        if r.random() < 0.5:
            m = 0
            while m == 0: m = sum(1 << c for c in range(7) if r.random() < 0.35)
            rules.append((m, 0, r.choice([1, 1, 2, 2, 3, 6])))
        else:
            cs = r.sample(range(7), 2)
            rules.append((1 << cs[0], 1 << cs[1], (1 << 24) - 1))
    return (cap, rules, _gen_runs(r, n))


EDGES = [
    (6, [], []), (6, [], [(0, 1)]), (1, [], [(0, 1), (1, 1), (2, 0)]),
    (6, [(1, 0, 1)], [(0, 1), (0, 1), (1, 1)]),                       # limit 1 on cat 0
    (6, [(1, 2, (1 << 24) - 1)], [(0, 1), (1, 1), (0, 1), (1, 1)]),   # apart 0/1 alternating
    (3, [], [(0, 5), (0, 0), (0, 0), (0, 0), (0, 0)]),                # unit larger than cap
    (6, [(1, 0, 2)], [(0, 3), (0, 0), (0, 0), (1, 1)]),               # unit of 3 with limit 2 -> chunked
    (4, [(3, 0, 2), (1, 4, (1 << 24) - 1)], [(0, 2), (0, 0), (1, 1), (2, 3), (2, 0), (2, 0), (0, 1)]),
    (6, [(127, 0, 6)], [(c, 1) for c in range(7)] * 3),
    (2, [(2, 0, 1)], [(1, 2), (1, 0), (0, 1), (1, 1)]),
    (6, [], [(0, 0), (0, 0), (1, 0)]),                                # s = 0 at the start
]

SIZES = [4, 8, 16, 32]
TEST_SIZES = [128, 320]


def make_program():
    from genome.corpus import REGISTRY, program
    pid = "hero1_sectioner"
    if pid in REGISTRY: return REGISTRY[pid]
    return program(pid, "T5", "HERO-1 sectioner: next-fit seating into sections with rule counters (see genome/hero1/lang.py).",
                   INP, OUT, _ref, _gen, SIZES, TEST_SIZES, edges=[e for e in EDGES])


def verify_kernel(seeds=(0, 1, 2), workers=6, timeout=60.0, net=None):
    from genome.verify import verify
    p = make_program(); res = []
    for s in seeds:
        t = time.time()
        r = verify(p, net or net_text(), s, timeout, workers=workers)
        r["seed"] = s; r["secs"] = round(time.time() - t, 1); res.append(r)
        print("seed", s, r["status"], r.get("cases"), r.get("failed"), r.get("metrics"), r.get("counterexample") or r.get("reason") or "", r["secs"], "s", flush=True)
    return res


if __name__ == "__main__":
    print(net_text()) if len(sys.argv) > 1 and sys.argv[1] == "net" else verify_kernel(tuple(int(a) for a in sys.argv[1:]) or (0, 1, 2))
