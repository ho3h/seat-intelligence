"""HERO-3 benchmark: fold programs, written BEFORE any tester or rewriter run (see docs/HERO-3.md section 1).

A fold is a monoid-shaped triple of nets plus a sequential step:
    unit   a closed literal of the state type
    lift   @lift = (x out)              element -> state
    comb   @comb = (a (b out))          state x state -> state      (the "combining step")
    fin    @fin  = (s out)              state -> output             (optional; identity if absent)
    step   @step = (acc (x out))        the sequential step; by default comb(acc, lift(x)); overridden where the
                                        author's sequential fold is written naturally and the combiner is a guess
The original (sequential) net is a one-cell-at-a-time list walker over `step` starting at `unit`; the rewriter builds
a balanced tree reduction over a tree-shaped input from lift/comb/fin. Labels (label, comm) are set here, before any run:
    assoc       comb is associative with unit as two-sided identity on all reachable states (by construction)
    nonassoc    comb is NOT associative (Python witness recorded in runs/hero3/PREREG.json before running)
    adversarial a planted single-point violation that no finite sample can be expected to find (excluded from kill rule (a),
                reported separately; declared in docs/HERO-3.md section 1)
States are numbers or right-nested tuples of numbers (arity k).
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Callable, Any
from ..types import u24, tup, MASK
from .netbuild import build, mx, mn, sel, eq, ne, le, ge, lnot, C

M = MASK
BIG = MASK
CAP = 1_000_000


def T(k): return u24 if k == 1 else tup(*([u24] * k))


def lit(v):
    """Python state value -> literal net text."""
    if isinstance(v, int): return str(v)
    v = list(v)
    return str(v[0]) if len(v) == 1 else f"({v[0]} {lit(v[1:])})"


@dataclass
class Fold:
    id: str
    label: str                       # assoc | nonassoc | adversarial
    desc: str
    elem_ar: int                     # 1 = number, 2 = pair
    state_ar: int
    unit: Any                        # python value (int or tuple)
    lift_txt: str
    comb_txt: str
    py_lift: Callable
    py_comb: Callable
    gen: Callable                    # gen(rng) -> element
    enum: list                       # small alphabet for exhaustive-small states
    out_ar: int = 0                  # 0 = same as state
    fin_txt: str | None = None
    py_fin: Callable | None = None
    step_txt: str | None = None      # overrides comb(acc, lift x)
    py_step: Callable | None = None
    py_ref: Callable | None = None   # natural reference on a whole list (overrides fold of py_step)
    comm: bool | None = None         # ground truth commutativity (assoc folds)
    corpus: str | None = None
    edges: list = field(default_factory=list)
    flavour: str = ""                # "seating" for the luncheon-flavoured ones
    note: str = ""
    inv: Callable | None = None      # optional element-domain check

    def __post_init__(self):
        if self.out_ar == 0: self.out_ar = self.state_ar if self.fin_txt is None else 1

    # ---- python semantics
    def state_of(self, xs):
        s = self.unit
        for x in xs: s = (self.py_step or (lambda a, y: self.py_comb(a, self.py_lift(y))))(s, x)
        return s

    def out_of_state(self, s): return self.py_fin(s) if self.py_fin else s

    def ref(self, xs):
        if self.py_ref: return self.py_ref(xs)
        return self.out_of_state(self.state_of(xs))

    def step_py(self, a, x):
        return self.py_step(a, x) if self.py_step else self.py_comb(a, self.py_lift(x))

    @property
    def elem_t(self): return T(self.elem_ar)
    @property
    def state_t(self): return T(self.state_ar)
    @property
    def out_t(self): return T(self.out_ar)
    @property
    def unit_txt(self): return lit(self.unit)


# ------------------------------------------------------------------------------------------- element generators
_EDGE = [0, 1, 2, BIG, BIG - 1, 1 << 23, (1 << 23) - 1, 1000, 999, 1001]


def g_mix(rng):
    r = rng.random()
    if r < 0.40: return rng.randrange(0, 11)
    if r < 0.70: return rng.randrange(0, 1001)
    if r < 0.90: return rng.randrange(0, M + 1)
    return rng.choice(_EDGE)


def g_small(k):
    def g(rng):
        return rng.randrange(k) if rng.random() < 0.85 else g_mix(rng)
    return g


def g_cat(rng): return rng.randrange(7)


def g_flag(rng): return 1 if rng.random() < 0.2 else 0


def g_flag_wide(rng):
    r = rng.random()
    return 0 if r < 0.7 else (1 if r < 0.9 else g_mix(rng))


def g_zero_heavy(rng): return 0 if rng.random() < 0.25 else g_mix(rng)


def g_gcd(rng):
    r = rng.random()
    if r < 0.35: return rng.randrange(0, 61)
    if r < 0.70: return rng.choice([6, 10, 15, 30, 12, 18]) * rng.randrange(0, 60)
    if r < 0.85: return rng.randrange(0, M + 1)
    return rng.choice(_EDGE)


def g_pair(rng): return (rng.randrange(6) if rng.random() < 0.7 else g_mix(rng), g_mix(rng))


def g_guest(rng): return (rng.randrange(10), rng.randrange(100))


ENUM3 = [0, 1, 2]

FOLDS: list[Fold] = []


def add(**kw):
    f = Fold(**kw)
    assert f.id not in {g.id for g in FOLDS}, f.id
    FOLDS.append(f)
    return f


def _sc(f):  # scalar helpers for lifts
    return f


# ============================================================================================ ASSOCIATIVE
LE = [[], [0], [BIG], [1, 1, 1]]

add(id="sum", label="assoc", comm=True, corpus="t1_sum", desc="sum of all elements mod 2^24",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: x),
    comb_txt=build("comb", [1, 1], lambda a, b: a + b), py_lift=lambda x: x, py_comb=lambda a, b: (a + b) & M,
    gen=g_mix, enum=ENUM3)

add(id="product", label="assoc", comm=True, corpus="t1_product", desc="product of all elements mod 2^24",
    elem_ar=1, state_ar=1, unit=1, lift_txt=build("lift", [1], lambda x: x),
    comb_txt=build("comb", [1, 1], lambda a, b: a * b), py_lift=lambda x: x, py_comb=lambda a, b: (a * b) & M,
    gen=g_mix, enum=ENUM3)

add(id="length", label="assoc", comm=True, corpus="t1_length", desc="number of elements",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: C(1)),
    comb_txt=build("comb", [1, 1], lambda a, b: a + b), py_lift=lambda x: 1, py_comb=lambda a, b: (a + b) & M,
    gen=g_mix, enum=ENUM3)

add(id="max", label="assoc", comm=True, corpus="t1_max", desc="largest element, 0 for the empty list",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: x),
    comb_txt=build("comb", [1, 1], lambda a, b: mx(a, b)), py_lift=lambda x: x, py_comb=max,
    gen=g_mix, enum=ENUM3)

add(id="min", label="assoc", comm=True, corpus="t1_min", desc="smallest element, 16777215 for the empty list",
    elem_ar=1, state_ar=1, unit=BIG, lift_txt=build("lift", [1], lambda x: x),
    comb_txt=build("comb", [1, 1], lambda a, b: mn(a, b)), py_lift=lambda x: x, py_comb=min,
    gen=g_mix, enum=ENUM3)

add(id="count_even", label="assoc", comm=True, corpus="t1_count_even", desc="number of even elements",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: (x % 2) ^ 1),
    comb_txt=build("comb", [1, 1], lambda a, b: a + b), py_lift=lambda x: 1 - x % 2, py_comb=lambda a, b: (a + b) & M,
    gen=g_mix, enum=ENUM3)


def _argmax(strict_gt):
    def comb(A, B):
        c = (B[0] > A[0]) if strict_gt else (B[0] < A[0])
        return (sel(c, B[0], A[0]), sel(c, A[2] + B[1], A[1]), A[2] + B[2])
    return comb


def _argmax_py(A, B):
    return (B[0], (A[2] + B[1]) & M, (A[2] + B[2]) & M) if B[0] > A[0] else (A[0], A[1], (A[2] + B[2]) & M)


def _argmin_py(A, B):
    return (B[0], (A[2] + B[1]) & M, (A[2] + B[2]) & M) if B[0] < A[0] else (A[0], A[1], (A[2] + B[2]) & M)


add(id="argmax_first", label="assoc", comm=False, corpus="t2_argmax", desc="index of the first occurrence of the largest element (0 if empty)",
    elem_ar=1, state_ar=3, unit=(0, 0, 0), lift_txt=build("lift", [1], lambda x: (x, C(0), C(1))),
    comb_txt=build("comb", [3, 3], _argmax(True)), py_lift=lambda x: (x, 0, 1), py_comb=_argmax_py,
    fin_txt=build("fin", [3], lambda s: s[1]), py_fin=lambda s: s[1], gen=g_small(6), enum=ENUM3, out_ar=1)

add(id="argmin_first", label="assoc", comm=False, corpus="t2_argmin", desc="index of the first occurrence of the smallest element (0 if empty)",
    elem_ar=1, state_ar=3, unit=(BIG, 0, 0), lift_txt=build("lift", [1], lambda x: (x, C(0), C(1))),
    comb_txt=build("comb", [3, 3], _argmax(False)), py_lift=lambda x: (x, 0, 1), py_comb=_argmin_py,
    fin_txt=build("fin", [3], lambda s: s[1]), py_fin=lambda s: s[1], gen=g_small(6), enum=ENUM3, out_ar=1)


def _second(a, b): return (max(a[0], b[0]), max(min(a[0], b[0]), max(a[1], b[1])))


add(id="second_largest", label="assoc", comm=True, corpus="t2_second_largest", desc="second largest element counting duplicates (0 if fewer than 2)",
    elem_ar=1, state_ar=2, unit=(0, 0), lift_txt=build("lift", [1], lambda x: (x, C(0))),
    comb_txt=build("comb", [2, 2], lambda a, b: (mx(a[0], b[0]), mx(mn(a[0], b[0]), mx(a[1], b[1])))),
    py_lift=lambda x: (x, 0), py_comb=_second, fin_txt=build("fin", [2], lambda s: s[1]), py_fin=lambda s: s[1],
    gen=g_small(8), enum=ENUM3, out_ar=1)


def _lr_net(A, B):
    ea, eb = eq(A[0], 0), eq(B[0], 0)
    j = eq(A[2], B[1])
    pre = A[3] + (eq(A[3], A[0]) & j) * B[3]
    suf = B[4] + (eq(B[4], B[0]) & j) * A[4]
    best = mx(mx(A[5], B[5]), j * (A[4] + B[3]))
    pick = lambda k, g: sel(ea, B[k], sel(eb, A[k], g))
    return (A[0] + B[0], pick(1, A[1]), pick(2, B[2]), pick(3, pre), pick(4, suf), pick(5, best))


def _lr_py(A, B):
    if A[0] == 0: return B
    if B[0] == 0: return A
    j = int(A[2] == B[1])
    pre = A[3] + (int(A[3] == A[0]) & j) * B[3]
    suf = B[4] + (int(B[4] == B[0]) & j) * A[4]
    best = max(A[5], B[5], j * (A[4] + B[3]))
    return ((A[0] + B[0]) & M, A[1], B[2], pre & M, suf & M, best & M)


add(id="longest_run", label="assoc", comm=False, corpus="t2_longest_run", desc="length of the longest run of equal consecutive elements",
    elem_ar=1, state_ar=6, unit=(0, 0, 0, 0, 0, 0), lift_txt=build("lift", [1], lambda x: (C(1), x, x, C(1), C(1), C(1))),
    comb_txt=build("comb", [6, 6], _lr_net), py_lift=lambda x: (1, x, x, 1, 1, 1), py_comb=_lr_py,
    fin_txt=build("fin", [6], lambda s: s[5]), py_fin=lambda s: s[5], gen=g_small(3), enum=ENUM3, out_ar=1)


def _is_net(A, B):
    ok_g = A[3] & B[3] & le(A[2], B[1])
    return (A[0] & B[0], sel(A[0], B[1], A[1]), sel(B[0], A[2], B[2]), sel(A[0], B[3], sel(B[0], A[3], ok_g)))


def _is_py(A, B):
    if A[0]: return B
    if B[0]: return A
    return (0, A[1], B[2], A[3] & B[3] & int(A[2] <= B[1]))


add(id="is_sorted", label="assoc", comm=False, corpus="t2_is_sorted", desc="1 if non-decreasing else 0",
    elem_ar=1, state_ar=4, unit=(1, 0, 0, 1), lift_txt=build("lift", [1], lambda x: (C(0), x, x, C(1))),
    comb_txt=build("comb", [4, 4], _is_net), py_lift=lambda x: (0, x, x, 1), py_comb=_is_py,
    fin_txt=build("fin", [4], lambda s: s[3]), py_fin=lambda s: s[3], gen=g_small(4), enum=ENUM3, out_ar=1)

add(id="last", label="assoc", comm=False, corpus="t1_last", desc="last element (0 if empty)",
    elem_ar=1, state_ar=2, unit=(0, 0), lift_txt=build("lift", [1], lambda x: (C(1), x)),
    comb_txt=build("comb", [2, 2], lambda A, B: (A[0] | B[0], sel(B[0], B[1], A[1]))),
    py_lift=lambda x: (1, x), py_comb=lambda A, B: (A[0] | B[0], B[1] if B[0] else A[1]),
    fin_txt=build("fin", [2], lambda s: s[1]), py_fin=lambda s: s[1], gen=g_mix, enum=ENUM3, out_ar=1)

add(id="xor_all", label="assoc", comm=True, desc="xor of all elements",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: x),
    comb_txt=build("comb", [1, 1], lambda a, b: a ^ b), py_lift=lambda x: x, py_comb=lambda a, b: a ^ b,
    gen=g_mix, enum=ENUM3, edges=LE + [[BIG, BIG]])

add(id="category_set", label="assoc", comm=True, flavour="seating", desc="bitset of the guest categories (0..6) present in a section (set union as bitset OR)",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: C(1) << x),
    comb_txt=build("comb", [1, 1], lambda a, b: a | b), py_lift=lambda x: 1 << x, py_comb=lambda a, b: a | b,
    gen=g_cat, enum=[0, 1, 2, 5], edges=[[], [0], [6, 6], [0, 1, 2, 3, 4, 5, 6]])

add(id="all_positive", label="assoc", comm=True, desc="1 if every element is positive else 0 (empty: 1)",
    elem_ar=1, state_ar=1, unit=1, lift_txt=build("lift", [1], lambda x: x > 0),
    comb_txt=build("comb", [1, 1], lambda a, b: a & b), py_lift=lambda x: int(x > 0), py_comb=lambda a, b: a & b,
    gen=g_zero_heavy, enum=ENUM3, edges=LE)

add(id="any_zero", label="assoc", comm=True, desc="1 if some element is zero else 0",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: eq(x, 0)),
    comb_txt=build("comb", [1, 1], lambda a, b: a | b), py_lift=lambda x: int(x == 0), py_comb=lambda a, b: a | b,
    gen=g_zero_heavy, enum=ENUM3, edges=LE)

add(id="count_gt500", label="assoc", comm=True, desc="number of elements greater than 500",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: x > 500),
    comb_txt=build("comb", [1, 1], lambda a, b: a + b), py_lift=lambda x: int(x > 500), py_comb=lambda a, b: (a + b) & M,
    gen=g_mix, enum=[0, 500, 501], edges=LE + [[500, 501, 499]])

add(id="sum_squares", label="assoc", comm=True, desc="sum of squares mod 2^24",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: x * x),
    comb_txt=build("comb", [1, 1], lambda a, b: a + b), py_lift=lambda x: (x * x) & M, py_comb=lambda a, b: (a + b) & M,
    gen=g_mix, enum=ENUM3)

GCD_COMB = """@comb = (a (b out))
  & b ~ {b1 b2}
  & b1 ~ ?((@gcd_z @gcd_s) (a (b2 out)))

@gcd_z = (a (* a))

@gcd_s = (* (a (b out)))
  & b ~ {b1 b2}
  & a ~ $([%] $(b1 r))
  & @comb ~ (b2 (r out))
"""
add(id="gcd", label="assoc", comm=True, desc="gcd of all elements (gcd of empty = 0)",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: x),
    comb_txt=GCD_COMB, py_lift=lambda x: x, py_comb=math.gcd, gen=g_gcd, enum=[0, 4, 6, 9], edges=LE + [[12, 18], [0, 0], [7]])


def _lex_min_net(A, B):
    c = (A[0] < B[0]) | (eq(A[0], B[0]) & le(A[1], B[1]))
    return (sel(c, A[0], B[0]), sel(c, A[1], B[1]))


add(id="lexmin_pair", label="assoc", comm=True, desc="lexicographic minimum of (a, b) pairs; (16777215, 16777215) if empty",
    elem_ar=2, state_ar=2, unit=(BIG, BIG), lift_txt=build("lift", [2], lambda p: (p[0], p[1])),
    comb_txt=build("comb", [2, 2], _lex_min_net), py_lift=lambda p: tuple(p), py_comb=lambda A, B: min(A, B),
    gen=g_pair, enum=[(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)], edges=[[], [(0, 0)], [(BIG, BIG)], [(1, 5), (1, 3), (0, 9)]])


def _top3_net(a, b):
    return (mx(a[0], b[0]), mx(mn(a[0], b[0]), mx(a[1], b[1])),
            mx(mx(a[2], b[2]), mx(mn(a[0], b[1]), mn(a[1], b[0]))))


def _top3_py(a, b):
    return (max(a[0], b[0]), max(min(a[0], b[0]), max(a[1], b[1])),
            max(max(a[2], b[2]), max(min(a[0], b[1]), min(a[1], b[0]))))


add(id="top3_merge", label="assoc", comm=True, desc="the three largest elements in descending order, zero padded (top-k merge, k=3)",
    elem_ar=1, state_ar=3, unit=(0, 0, 0), lift_txt=build("lift", [1], lambda x: (x, C(0), C(0))),
    comb_txt=build("comb", [3, 3], _top3_net), py_lift=lambda x: (x, 0, 0), py_comb=_top3_py,
    gen=g_small(9), enum=ENUM3, edges=LE + [[5, 5, 5, 5], [1, 2, 3, 4]],
    py_ref=lambda xs: tuple((sorted(xs, reverse=True) + [0, 0, 0])[:3]))

add(id="sat_sum_cap", label="assoc", comm=True, desc="sum capped at 1,000,000 (saturating), elements clamped first",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: mn(x, CAP)),
    comb_txt=build("comb", [1, 1], lambda a, b: mn(a + b, CAP)), py_lift=lambda x: min(x, CAP), py_comb=lambda a, b: min(a + b, CAP),
    gen=g_mix, enum=[0, 1, 600000], edges=LE + [[CAP, CAP], [600000, 600000, 5]])


def _sat24(a, b):
    c = a + b
    return sel(c < a, C(BIG), c)


add(id="sat_sum_24", label="assoc", comm=True, desc="saturating sum over the full 24-bit range (overflow is detected and clamps to 16777215)",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: x),
    comb_txt=build("comb", [1, 1], _sat24), py_lift=lambda x: x, py_comb=lambda a, b: min(a + b, BIG),
    gen=g_mix, enum=[0, 1, BIG], edges=LE + [[BIG, 1], [1 << 23, 1 << 23], [1 << 23, (1 << 23) - 1]])

add(id="minmax_pair", label="assoc", comm=True, desc="(min, max) of the list; (16777215, 0) if empty",
    elem_ar=1, state_ar=2, unit=(BIG, 0), lift_txt=build("lift", [1], lambda x: (x, x)),
    comb_txt=build("comb", [2, 2], lambda a, b: (mn(a[0], b[0]), mx(a[1], b[1]))),
    py_lift=lambda x: (x, x), py_comb=lambda a, b: (min(a[0], b[0]), max(a[1], b[1])), gen=g_mix, enum=ENUM3)

add(id="mean_floor", label="assoc", comm=True, desc="floor(sum / count), sum mod 2^24, via a (sum, count) state with the correct merge",
    elem_ar=1, state_ar=2, unit=(0, 0), lift_txt=build("lift", [1], lambda x: (x, C(1))),
    comb_txt=build("comb", [2, 2], lambda a, b: (a[0] + b[0], a[1] + b[1])),
    py_lift=lambda x: (x, 1), py_comb=lambda a, b: ((a[0] + b[0]) & M, a[1] + b[1]),
    fin_txt=build("fin", [2], lambda s: s[0] // mx(s[1], 1)), py_fin=lambda s: s[0] // max(s[1], 1), gen=g_mix, enum=ENUM3, out_ar=1)

add(id="hash_affine", label="assoc", comm=False, desc="order-dependent hash h = h*31 + x, parallelised as composition of affine maps (m, a)",
    elem_ar=1, state_ar=2, unit=(1, 0), lift_txt=build("lift", [1], lambda x: (C(31), x)),
    comb_txt=build("comb", [2, 2], lambda A, B: (A[0] * B[0], A[1] * B[0] + B[1])),
    py_lift=lambda x: (31, x), py_comb=lambda A, B: ((A[0] * B[0]) & M, (A[1] * B[0] + B[1]) & M),
    fin_txt=build("fin", [2], lambda s: s[1]), py_fin=lambda s: s[1], gen=g_mix, enum=ENUM3, out_ar=1)


def _ae_net(A, B, wrong=False):
    ea, eb = eq(A[0], 0), eq(B[0], 0)
    j = eq(A[2], B[2] if wrong else B[1])
    return (A[0] + B[0], sel(ea, B[1], A[1]), sel(eb, A[2], B[2]), sel(ea, B[3], sel(eb, A[3], A[3] + B[3] + j)))


def _ae_py(A, B, wrong=False):
    if A[0] == 0: return B
    if B[0] == 0: return A
    j = int(A[2] == (B[2] if wrong else B[1]))
    return ((A[0] + B[0]) & M, A[1], B[2], (A[3] + B[3] + j) & M)


add(id="adjacent_equal", label="assoc", comm=False, flavour="seating", desc="number of adjacent equal pairs (neighbouring seats with the same category), correct merge (len, first, last, count)",
    elem_ar=1, state_ar=4, unit=(0, 0, 0, 0), lift_txt=build("lift", [1], lambda x: (C(1), x, x, C(0))),
    comb_txt=build("comb", [4, 4], _ae_net), py_lift=lambda x: (1, x, x, 0), py_comb=_ae_py,
    fin_txt=build("fin", [4], lambda s: s[3]), py_fin=lambda s: s[3], gen=g_small(3), enum=ENUM3, out_ar=1)


def _cat_lift(x): return tuple(eq(x, k) for k in range(7))


add(id="category_counts", label="assoc", comm=True, flavour="seating", desc="count of guests in each of the 7 categories of a section (7-tuple)",
    elem_ar=1, state_ar=7, unit=(0,) * 7, lift_txt=build("lift", [1], _cat_lift),
    comb_txt=build("comb", [7, 7], lambda a, b: tuple(a[i] + b[i] for i in range(7))),
    py_lift=lambda x: tuple(int(x == k) for k in range(7)), py_comb=lambda a, b: tuple((a[i] + b[i]) & M for i in range(7)),
    gen=g_cat, enum=[0, 1, 6], edges=[[], [0], [6, 6, 6], [0, 1, 2, 3, 4, 5, 6]])


def _mp_net(A, B):
    c = (A[0] > B[0]) | (eq(A[0], B[0]) & le(A[1], B[1]))
    return (sel(c, A[0], B[0]), sel(c, A[1], B[1]))


def _mp_py(A, B):
    return A if (A[0] > B[0] or (A[0] == B[0] and A[1] <= B[1])) else B


add(id="max_priority_guest", label="assoc", comm=True, flavour="seating", desc="(priority, id) of the highest-priority guest, ties to the smaller id; (0, 16777215) if empty",
    elem_ar=2, state_ar=2, unit=(0, BIG), lift_txt=build("lift", [2], lambda p: (p[0], p[1])),
    comb_txt=build("comb", [2, 2], _mp_net), py_lift=lambda p: tuple(p), py_comb=_mp_py, gen=g_guest,
    enum=[(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)], edges=[[], [(3, 4)], [(3, 4), (3, 2)], [(0, 5), (0, 5)]])


def _fv_net(A, B):
    ha, hb = ne(A[1], BIG), ne(B[1], BIG)
    return (A[0] + B[0], sel(ha, A[1], sel(hb, A[0] + B[1], C(BIG))))


def _fv_py(A, B):
    return ((A[0] + B[0]) & M, A[1] if A[1] != BIG else ((A[0] + B[1]) & M if B[1] != BIG else BIG))


add(id="first_violation", label="assoc", comm=False, flavour="seating", desc="index of the first rule violation (element != 0) in seat order; 16777215 if none",
    elem_ar=1, state_ar=2, unit=(0, BIG), lift_txt=build("lift", [1], lambda x: (C(1), sel(ne(x, 0), C(0), C(BIG)))),
    comb_txt=build("comb", [2, 2], _fv_net), py_lift=lambda x: (1, 0 if x != 0 else BIG), py_comb=_fv_py,
    fin_txt=build("fin", [2], lambda s: s[1]), py_fin=lambda s: s[1], gen=g_flag_wide, enum=ENUM3, out_ar=1,
    edges=[[], [0], [1], [0, 0, 1], [0, 0, 0], [7]],
    py_ref=lambda xs: next((i for i, x in enumerate(xs) if x != 0), BIG))

add(id="section_fill_cap6", label="assoc", comm=True, flavour="seating", desc="guests in a section counted up to the section limit of 6 (saturating count)",
    elem_ar=1, state_ar=1, unit=0, lift_txt=build("lift", [1], lambda x: C(1)),
    comb_txt=build("comb", [1, 1], lambda a, b: mn(a + b, 6)), py_lift=lambda x: 1, py_comb=lambda a, b: min(a + b, 6),
    gen=g_mix, enum=ENUM3, edges=LE + [[1] * 6, [1] * 7])

# ============================================================================================ NON-ASSOCIATIVE (must be rejected)
def _nonassoc(id, desc, comb_net, comb_py, unit=0, gen=g_mix, enum=ENUM3, label="nonassoc", **kw):
    return add(id=id, label=label, desc=desc, elem_ar=1, state_ar=1, unit=unit, lift_txt=build("lift", [1], lambda x: x),
               comb_txt=build("comb", [1, 1], comb_net), py_lift=lambda x: x, py_comb=comb_py, gen=gen, enum=enum, **kw)


_nonassoc("sub_fold", "left fold with subtraction, acc - x", lambda a, b: a - b, lambda a, b: (a - b) & M)
_nonassoc("hash31", "order-dependent hash h = h*31 + x used directly as the combiner", lambda a, b: a * 31 + b, lambda a, b: (a * 31 + b) & M)
_nonassoc("abs_diff", "fold with |acc - x|", lambda a, b: sel(a > b, a - b, b - a), lambda a, b: abs(a - b))
_nonassoc("alternating", "alternating difference, b - a", lambda a, b: b - a, lambda a, b: (b - a) & M)
_nonassoc("sat_sub", "saturating subtraction max(a - b, 0)", lambda a, b: sel(a > b, a - b, C(0)), lambda a, b: max(a - b, 0))
_nonassoc("horner_square", "a*a + b", lambda a, b: a * a + b, lambda a, b: (a * a + b) & M)
_nonassoc("xorshift_hash", "rolling hash (a << 1) ^ b", lambda a, b: (a << 1) ^ b, lambda a, b: ((a << 1) & M) ^ b)
_nonassoc("midpoint", "running midpoint (a + b) >> 1", lambda a, b: (a + b) >> 1, lambda a, b: ((a + b) & M) >> 1)
_nonassoc("sat_sum_unclamped", "saturating sum at 1,000,000 with NO element clamp (wide values wrap first)",
          lambda a, b: mn(a + b, CAP), lambda a, b: min((a + b) & M, CAP))
_nonassoc("glitch_1e3", "sum with a merge bug that fires on about 1 pair in 1000 ((a&63)==63 and (b&15)==15 gives 0)",
          lambda a, b: sel(eq(a & 63, 63) & eq(b & 15, 15), C(0), a + b),
          lambda a, b: 0 if (a & 63) == 63 and (b & 15) == 15 else (a + b) & M, gen=g_mix)
_nonassoc("planted_point", "sum with a planted single-point merge bug at (12345678, 8765432); NO finite sample is expected to find it",
          lambda a, b: sel(eq(a, 12345678) & eq(b, 8765432), C(0), a + b),
          lambda a, b: 0 if (a == 12345678 and b == 8765432) else (a + b) & M, label="adversarial")

# running average: natural sequential step, wrong (unweighted) merge
add(id="avg_wrong_merge", label="nonassoc", desc="running average (sequential step (m*n + x)/(n+1)) with the tempting unweighted merge ((m1+m2)/2, n1+n2)",
    elem_ar=1, state_ar=2, unit=(0, 0), lift_txt=build("lift", [1], lambda x: (x, C(1))),
    comb_txt=build("comb", [2, 2], lambda A, B: ((A[0] + B[0]) >> 1, A[1] + B[1])),
    py_lift=lambda x: (x, 1), py_comb=lambda A, B: (((A[0] + B[0]) & M) >> 1, A[1] + B[1]),
    step_txt=build("step", [2, 1], lambda s, x: ((s[0] * s[1] + x) // (s[1] + 1), s[1] + 1)),
    py_step=lambda s, x: (((s[0] * s[1] + x) & M) // (s[1] + 1), s[1] + 1),
    fin_txt=build("fin", [2], lambda s: s[0]), py_fin=lambda s: s[0], gen=g_mix, enum=ENUM3, out_ar=1)

# adjacent equal pairs: correct sequential step, wrong merge (compares last with last)
add(id="adjacent_equal_wrong", label="nonassoc", flavour="seating",
    desc="adjacent-equal count: correct sequential step, tempting merge compares A.last with B.last instead of B.first",
    elem_ar=1, state_ar=4, unit=(0, 0, 0, 0), lift_txt=build("lift", [1], lambda x: (C(1), x, x, C(0))),
    comb_txt=build("comb", [4, 4], lambda A, B: _ae_net(A, B, wrong=True)),
    py_lift=lambda x: (1, x, x, 0), py_comb=lambda A, B: _ae_py(A, B, wrong=True),
    step_txt=build("step", [4, 1], lambda s, x: _ae_net(s, (C(1), x, x, C(0)))),
    py_step=lambda s, x: _ae_py(s, (1, x, x, 0)),
    fin_txt=build("fin", [4], lambda s: s[3]), py_fin=lambda s: s[3], gen=g_small(3), enum=ENUM3, out_ar=1)


def by_id(i): return next(f for f in FOLDS if f.id == i)


def assoc(): return [f for f in FOLDS if f.label == "assoc"]
def nonassoc(): return [f for f in FOLDS if f.label == "nonassoc"]
def adversarial(): return [f for f in FOLDS if f.label == "adversarial"]


if __name__ == "__main__":
    print(len(FOLDS), "folds:", len(assoc()), "assoc,", len(nonassoc()), "nonassoc,", len(adversarial()), "adversarial")
