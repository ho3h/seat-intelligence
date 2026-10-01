"""Task generator: thousands of distinct, verifiable contracts composed from parameterised stages.

Every task's description and reference are built from the same stage objects, so they cannot drift apart. Tasks are
deterministic in (family, index). Families are split: TRAIN families feed training and tuning; HOLDOUT families are never
seen by anything that trains or tunes (they, and the original 200-program corpus, are the test).
"""
from __future__ import annotations
import hashlib, random
from .corpus import Program
from .types import u24, list_of, tup, tree_of, MASK

M = MASK + 1  # 2^24
L = list_of(u24)
T = tree_of(u24)
BIG = MASK

TRAIN_FAMILIES = ["pipeline", "reduce", "scan", "position", "sortlike", "arith", "rangefn", "treefold"]
HOLDOUT_FAMILIES = ["zip2", "group", "treemap", "treetrav", "recon_count", "recon_uf"]


def _rng(family, idx, salt=""):
    h = hashlib.sha256(f"{family}|{idx}|{salt}".encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


# ------------------------------------------------------------------ list stages: (description, function)
def _pred(r):
    k = r.choice([3, 5, 10, 20, 50, 100, 500]); m = r.choice([2, 3, 4, 5, 7]); rem = r.randrange(m)
    return r.choice([
        (f"x > {k}", lambda x, k=k: x > k), (f"x < {k}", lambda x, k=k: x < k), (f"x >= {k}", lambda x, k=k: x >= k),
        ("x is even", lambda x: x % 2 == 0), ("x is odd", lambda x: x % 2 == 1),
        (f"x mod {m} equals {rem}", lambda x, m=m, rem=rem: x % m == rem)])


def _map(r):
    a = r.choice([2, 3, 5, 7, 10]); b = r.choice([0, 1, 2, 7, 100]); mk = r.choice([1, 3, 7, 15, 63, 255]); c = r.choice([1, 2, 5, 9])
    return r.choice([
        (f"x*{a}+{b} (mod 2^24)", lambda x, a=a, b=b: (x * a + b) % M),
        (f"x xor {mk}", lambda x, mk=mk: x ^ mk), (f"x and {mk}", lambda x, mk=mk: x & mk),
        (f"x+{c} (mod 2^24)", lambda x, c=c: (x + c) % M), ("x*x (mod 2^24)", lambda x: x * x % M),
        (f"x mod {a + 1}", lambda x, a=a: x % (a + 1)), (f"x integer-divided by {a}", lambda x, a=a: x // a)])


def _stage(r):
    k = r.choice([1, 2, 3, 5, 8])
    opts = [
        lambda: (lambda pd, pf: (f"keep only the elements x for which {pd}", lambda xs: [x for x in xs if pf(x)]))(*_pred(r)),
        lambda: (lambda md, mf: (f"replace every element x by {md}", lambda xs: [mf(x) for x in xs]))(*_map(r)),
        lambda: (f"keep only the first {k} elements (all of them if there are fewer)", lambda xs: xs[:k]),
        lambda: (f"remove the first {k} elements (nothing is removed if there are fewer)", lambda xs: xs[k:]),
        lambda: ("reverse the order", lambda xs: xs[::-1]),
        lambda: ("collapse every run of equal consecutive elements into a single element", lambda xs: [x for i, x in enumerate(xs) if i == 0 or xs[i - 1] != x]),
        lambda: ("replace the list by its running totals (element i becomes the sum of elements 0..i, mod 2^24)",
                 lambda xs: [sum(xs[:i + 1]) % M for i in range(len(xs))]),
        lambda: ("sort ascending", lambda xs: sorted(xs)),
    ]
    return r.choice(opts)()


REDUCERS = [
    ("the sum of all elements, mod 2^24 (0 for an empty list)", lambda xs: sum(xs) % M),
    ("the number of elements", len),
    ("the largest element (0 for an empty list)", lambda xs: max(xs, default=0)),
    ("the smallest element (16777215 for an empty list)", lambda xs: min(xs, default=BIG)),
    ("the bitwise xor of all elements (0 for an empty list)", lambda xs: __import__("functools").reduce(lambda a, b: a ^ b, xs, 0)),
    ("the last element (0 for an empty list)", lambda xs: xs[-1] if xs else 0),
    ("the first element (0 for an empty list)", lambda xs: xs[0] if xs else 0),
    ("the number of elements that are greater than the first element (0 for an empty list)", lambda xs: sum(1 for x in xs[1:] if x > xs[0]) if xs else 0),
]


def _list_gen(r):
    hi = r.choice([10, 30, 100, 1000])
    return lambda rng, n: [rng.randrange(hi) for _ in range(n)]


SIZES_L = list(range(0, 17)); TEST_L = [128, 256]
EDGE_L = [[], [0], [BIG], [1, 1, 1], [5, 3, 5, 9, 0]]


def _mk(id, desc, inp, out, ref, gen, sizes, tests, edges, pre=None):
    return Program(id, "GEN", desc, inp, out, ref, gen, list(sizes), list(tests), edges, pre)


def _num_prefix(steps):
    return "Start with the input list. Apply these steps in order:\n" + "\n".join(f"{i + 1}. {d}" for i, (d, _) in enumerate(steps))


# ------------------------------------------------------------------ families
def fam_pipeline(idx):
    r = _rng("pipeline", idx); steps = [_stage(r) for _ in range(r.choice([1, 2, 3]))]
    def ref(xs):
        for _, f in steps: xs = f(xs)
        return xs
    pr = _mk(f"gen_pipeline_{idx:05d}", _num_prefix(steps) + "\nOutput the resulting list.", L, L, ref, _list_gen(r), SIZES_L, TEST_L, EDGE_L)
    pr.steps = steps  # exposed so verified nets can be composed into deeper pipelines (genome/compose.py)
    return pr


def pipeline_from_steps(steps, name, hi=100):
    def ref(xs):
        for _, f in steps: xs = f(xs)
        return xs
    return _mk(name, _num_prefix(steps) + "\nOutput the resulting list.", L, L, ref, lambda rng, n: [rng.randrange(hi) for _ in range(n)], SIZES_L, TEST_L, EDGE_L)


def fam_reduce(idx):
    r = _rng("reduce", idx); steps = [_stage(r) for _ in range(r.choice([0, 1, 2]))]; rd, rf = r.choice(REDUCERS)
    def ref(xs):
        for _, f in steps: xs = f(xs)
        return rf(xs)
    pre = _num_prefix(steps) + "\n" if steps else "Use the input list as it is.\n"
    return _mk(f"gen_reduce_{idx:05d}", pre + f"Output {rd}.", L, u24, ref, _list_gen(r), SIZES_L, TEST_L, EDGE_L)


def fam_scan(idx):
    r = _rng("scan", idx)
    kind = r.choice(["runmax", "runmin", "diff", "runxor", "prefix_pred_count"])
    if kind == "runmax": d, f = "Output the running maximum: element i is the largest of elements 0..i.", lambda xs: [max(xs[:i + 1]) for i in range(len(xs))]
    elif kind == "runmin": d, f = "Output the running minimum: element i is the smallest of elements 0..i.", lambda xs: [min(xs[:i + 1]) for i in range(len(xs))]
    elif kind == "diff": d, f = "Output the list of differences xs[i+1] - xs[i] (mod 2^24) for every adjacent pair; the output has one element fewer than the input (empty for inputs of length 0 or 1).", lambda xs: [(xs[i + 1] - xs[i]) % M for i in range(len(xs) - 1)]
    elif kind == "runxor": d, f = "Output the running bitwise xor: element i is the xor of elements 0..i.", lambda xs: [__import__("functools").reduce(lambda a, b: a ^ b, xs[:i + 1]) for i in range(len(xs))]
    else:
        pd, pf = _pred(r)
        d, f = f"Output, for each position i, how many of the elements 0..i satisfy: {pd} (x is the element).", lambda xs, pf=pf: [sum(1 for x in xs[:i + 1] if pf(x)) for i in range(len(xs))]
    return _mk(f"gen_scan_{idx:05d}", d, L, L, f, _list_gen(r), SIZES_L, TEST_L, EDGE_L)


def fam_position(idx):
    r = _rng("position", idx); pd, pf = _pred(r); kind = r.choice(["first", "last", "count", "any_index_max", "first_max"])
    if kind == "first": d, f = f"Output the index (counting from 0) of the first element x for which {pd}; output 16777215 if there is none.", lambda xs: next((i for i, x in enumerate(xs) if pf(x)), BIG)
    elif kind == "last": d, f = f"Output the index (counting from 0) of the last element x for which {pd}; output 16777215 if there is none.", lambda xs: max((i for i, x in enumerate(xs) if pf(x)), default=BIG)
    elif kind == "count": d, f = f"Output the number of elements x for which {pd}.", lambda xs: sum(1 for x in xs if pf(x))
    elif kind == "first_max": d, f = "Output the index (counting from 0) of the first occurrence of the largest element; output 0 for an empty list.", lambda xs: xs.index(max(xs)) if xs else 0
    else: d, f = f"Output the sum of the indices (counting from 0) of the elements x for which {pd}, mod 2^24.", lambda xs: sum(i for i, x in enumerate(xs) if pf(x)) % M
    return _mk(f"gen_position_{idx:05d}", d, L, u24, f, _list_gen(r), SIZES_L, TEST_L, EDGE_L)


def fam_sortlike(idx):
    r = _rng("sortlike", idx); k = r.choice([1, 2, 3, 4]); kind = r.choice(["kth", "topk", "median", "dedup", "second"])
    if kind == "kth": return _mk(f"gen_sortlike_{idx:05d}", f"Output the element at index {k} (counting from 0) of the input sorted ascending; output 0 if the list has {k} or fewer elements.", L, u24, lambda xs: sorted(xs)[k] if len(xs) > k else 0, _list_gen(r), SIZES_L, TEST_L, EDGE_L)
    if kind == "topk": return _mk(f"gen_sortlike_{idx:05d}", f"Output the {k} largest elements in descending order (all elements in descending order if there are fewer than {k}).", L, L, lambda xs: sorted(xs, reverse=True)[:k], _list_gen(r), SIZES_L, TEST_L, EDGE_L)
    if kind == "median": return _mk(f"gen_sortlike_{idx:05d}", "Output the element at index len//2 (counting from 0, integer division) of the input sorted ascending; output 0 for an empty list.", L, u24, lambda xs: sorted(xs)[len(xs) // 2] if xs else 0, _list_gen(r), SIZES_L, TEST_L, EDGE_L)
    if kind == "dedup": return _mk(f"gen_sortlike_{idx:05d}", "Output the distinct values of the input in ascending order.", L, L, lambda xs: sorted(set(xs)), _list_gen(r), SIZES_L, TEST_L, EDGE_L)
    return _mk(f"gen_sortlike_{idx:05d}", "Output the largest value that is strictly smaller than the maximum; output 0 if there is no such value.", L, u24, lambda xs: max((x for x in xs if x < max(xs)), default=0) if xs else 0, _list_gen(r), SIZES_L, TEST_L, EDGE_L)


def _digit_sum(x, b):
    s = 0
    while x: s += x % b; x //= b
    return s


def fam_arith(idx):
    r = _rng("arith", idx); kind = r.choice(["digsum", "gcdmod", "powmod", "isqrt", "bitlen", "lcm", "trailing", "tri"])
    if kind == "digsum":
        b = r.choice([2, 3, 5, 7, 8, 10, 16]); return _mk(f"gen_arith_{idx:05d}", f"Output the sum of the digits of the input in base {b}.", u24, u24, lambda x: _digit_sum(x, b), lambda rng, n: rng.randrange(0, 2 ** n), range(1, 13), [16, 20], [0, 1, 255, BIG])
    if kind == "gcdmod":
        m = r.choice([7, 10, 12, 100, 255]); import math
        return _mk(f"gen_arith_{idx:05d}", f"Input is (a, b). Output gcd(a, b) mod {m} (gcd(a, 0) = a, gcd(0, 0) = 0).", tup(u24, u24), u24, lambda p: math.gcd(*p) % m, lambda rng, n: (rng.randrange(0, 2 ** n), rng.randrange(0, 2 ** n)), range(1, 13), [16, 20], [(0, 0), (0, 5), (12, 18), (BIG, 1)])
    if kind == "powmod":
        m = r.choice([7, 10, 13, 97, 1000, 4096]); return _mk(f"gen_arith_{idx:05d}", f"Input is (base, exp). Output base^exp mod {m} (0^0 counts as 1).", tup(u24, u24), u24, lambda p: pow(p[0], p[1], m), lambda rng, n: (rng.randrange(0, 2 ** 12), rng.randrange(0, 2 ** n)), range(1, 11), [14, 18], [(0, 0), (2, 10), (5, 0), (4095, 4095)])
    if kind == "isqrt":
        import math; return _mk(f"gen_arith_{idx:05d}", "Output the integer square root of the input: the largest integer s with s*s <= input.", u24, u24, math.isqrt, lambda rng, n: rng.randrange(0, 2 ** (2 * n)), range(1, 9), [11, 12], [0, 1, 2, 15, 16, BIG])
    if kind == "bitlen":
        return _mk(f"gen_arith_{idx:05d}", "Output the number of binary digits of the input (0 has 0 digits, 1 has 1, 5 has 3).", u24, u24, lambda x: x.bit_length(), lambda rng, n: rng.randrange(0, 2 ** n), range(1, 13), [16, 22], [0, 1, 2, 255, 256, BIG])
    if kind == "lcm":
        import math; return _mk(f"gen_arith_{idx:05d}", "Input is (a, b), both at most 4095. Output the least common multiple of a and b, or 0 if either is 0.", tup(u24, u24), u24, lambda p: 0 if 0 in p else p[0] * p[1] // math.gcd(*p), lambda rng, n: (rng.randrange(0, 2 ** n), rng.randrange(0, 2 ** n)), range(1, 13), [12, 12], [(0, 5), (4, 6), (4095, 4094), (1, 1)], pre=lambda p: p[0] < 4096 and p[1] < 4096)
    if kind == "trailing":
        def tz(x): return 0 if x == 0 else (x & -x).bit_length() - 1
        return _mk(f"gen_arith_{idx:05d}", "Output the number of trailing zero bits of the input in binary; output 0 for input 0.", u24, u24, tz, lambda rng, n: rng.randrange(0, 2 ** n), range(1, 13), [16, 22], [0, 1, 2, 8, 12, 2 ** 23])
    return _mk(f"gen_arith_{idx:05d}", "Input is n. Output 1+2+...+n (mod 2^24).", u24, u24, lambda n: n * (n + 1) // 2 % M, lambda rng, n: rng.randrange(0, 2 ** n), range(1, 13), [16, 22], [0, 1, 2, 4095, BIG])


def fam_rangefn(idx):
    r = _rng("rangefn", idx); a = r.choice([2, 3, 5, 7]); b = r.choice([0, 1, 4]); mk = r.choice([3, 7, 15]); mm = r.choice([5, 7, 10, 16])
    kinds = [(f"i*{a}+{b} (mod 2^24)", lambda i: (i * a + b) % M), ("i*i (mod 2^24)", lambda i: i * i % M), (f"i xor {mk}", lambda i: i ^ mk),
             (f"i mod {mm}", lambda i: i % mm), ("the number of one bits of i", lambda i: bin(i).count("1")), ("i*(i+1)/2 (mod 2^24)", lambda i: i * (i + 1) // 2 % M)]
    d, f = r.choice(kinds)
    return _mk(f"gen_rangefn_{idx:05d}", f"Input is n. Output the list of length n whose element at index i (counting from 0) is {d}.", u24, L, lambda n: [f(i) for i in range(n)], lambda rng, n: n, SIZES_L, [100, 256], [0, 1, 2])


def _tree_gen(rng, n):
    if n <= 0: return (0,)
    left = rng.randrange(0, n); return (1, _tree_gen(rng, left), rng.randrange(100), _tree_gen(rng, n - 1 - left))


TS = list(range(0, 12)); TT = [90, 180]; EDGE_T = [(0,), (1, (0,), 5, (0,)), (1, (1, (0,), 2, (0,)), 7, (0,)), (1, (0,), BIG, (1, (0,), 0, (0,)))]


def _folds(r):
    pd, pf = _pred(r)
    def h(t): return 0 if t[0] == 0 else 1 + max(h(t[1]), h(t[3]))
    def walk(t, acc, depth=0):
        if t[0] == 1: walk(t[1], acc, depth + 1); acc.append((t[2], depth)); walk(t[3], acc, depth + 1)
        return acc
    return r.choice([
        (f"the number of Nodes whose value x satisfies: {pd}", lambda t: sum(1 for v, _ in walk(t, []) if pf(v))),
        ("the sum of all values, mod 2^24", lambda t: sum(v for v, _ in walk(t, [])) % M),
        ("the largest value (0 for a Leaf)", lambda t: max((v for v, _ in walk(t, [])), default=0)),
        ("the smallest value (16777215 for a Leaf)", lambda t: min((v for v, _ in walk(t, [])), default=BIG)),
        ("the height (a Leaf has height 0, a Node has 1 + the larger height of its children)", h),
        ("the number of Leaf constructors", lambda t: len(walk(t, [])) + 1),
        ("the sum over all Nodes of value * (depth + 1), mod 2^24, where the root has depth 0", lambda t: sum(v * (d + 1) for v, d in walk(t, [])) % M)])


TREE_DESC = "A tree is Leaf or Node(left, value, right) with value a u24 (as a value: Leaf = (0,), Node = (1, left, value, right)). "


def fam_treefold(idx):
    r = _rng("treefold", idx); d, f = _folds(r)
    return _mk(f"gen_treefold_{idx:05d}", TREE_DESC + f"Output {d}.", T, u24, f, _tree_gen, TS, TT, EDGE_T)


def fam_treemap(idx):
    r = _rng("treemap", idx); md, mf = _map(r); kind = r.choice(["map", "mirror", "prune", "mapmirror"])
    def mp(t, f): return t if t[0] == 0 else (1, mp(t[1], f), f(t[2]), mp(t[3], f))
    def mir(t): return t if t[0] == 0 else (1, mir(t[3]), t[2], mir(t[1]))
    k = r.choice([10, 30, 60])
    def prune(t): return t if t[0] == 0 else ((0,) if t[2] > k else (1, prune(t[1]), t[2], prune(t[3])))
    if kind == "map": d, f = f"Output the tree of the same shape in which every value x is replaced by {md}.", lambda t: mp(t, mf)
    elif kind == "mirror": d, f = "Output the mirror image: the left and right children are swapped at every Node.", mir
    elif kind == "prune": d, f = f"Output the tree in which every Node whose value is greater than {k} is replaced by a Leaf (its whole subtree disappears); Nodes with smaller or equal values keep their processed children.", prune
    else: d, f = f"Output the mirror image (children swapped at every Node) with every value x replaced by {md}.", lambda t: mir(mp(t, mf))
    return _mk(f"gen_treemap_{idx:05d}", TREE_DESC + d, T, T, f, _tree_gen, TS, TT, EDGE_T)


def fam_treetrav(idx):
    r = _rng("treetrav", idx); pd, pf = _pred(r); kind = r.choice(["inorder", "preorder", "postorder", "leaves"])
    def io(t): return [] if t[0] == 0 else io(t[1]) + [t[2]] + io(t[3])
    def pre(t): return [] if t[0] == 0 else [t[2]] + pre(t[1]) + pre(t[3])
    def post(t): return [] if t[0] == 0 else post(t[1]) + post(t[3]) + [t[2]]
    def leaves(t): return [] if t[0] == 0 else ([t[2]] if t[1][0] == 0 and t[3][0] == 0 else leaves(t[1]) + leaves(t[3]))
    fn = {"inorder": io, "preorder": pre, "postorder": post, "leaves": leaves}[kind]
    nm = {"inorder": "in-order (left subtree, value, right subtree)", "preorder": "pre-order (value, left subtree, right subtree)",
          "postorder": "post-order (left subtree, right subtree, value)", "leaves": "left-to-right order, listing only the values of Nodes that have two Leaf children"}[kind]
    if kind == "leaves": d = f"Output the values of the Nodes that have two Leaf children, in left-to-right order, keeping only those values x for which {pd}."
    else: d = f"Traverse the tree {nm} and output the list of values x for which {pd}, in traversal order."
    return _mk(f"gen_treetrav_{idx:05d}", TREE_DESC + d, T, L, lambda t: [v for v in fn(t) if pf(v)], _tree_gen, TS, TT, EDGE_T)


def fam_zip2(idx):
    r = _rng("zip2", idx)
    ops = [("x + y (mod 2^24)", lambda x, y: (x + y) % M), ("x - y (mod 2^24)", lambda x, y: (x - y) % M), ("x * y (mod 2^24)", lambda x, y: x * y % M),
           ("the larger of x and y", max), ("the smaller of x and y", min), ("x xor y", lambda x, y: x ^ y), ("1 if x > y else 0", lambda x, y: int(x > y))]
    od, of = r.choice(ops); rd, rf = r.choice([(None, None)] + REDUCERS[:5])
    hi = r.choice([10, 100, 1000])
    def ref(p):
        zs = [of(x, y) for x, y in zip(*p)]
        return zs if rd is None else rf(zs)
    d = f"Input is (xs, ys). Pair the elements at equal positions (stop at the shorter list); for each pair (x from xs, y from ys) compute {od}. "
    d += "Output the list of results." if rd is None else f"Then output {rd}, of the list of results."
    return _mk(f"gen_zip2_{idx:05d}", d, tup(L, L), L if rd is None else u24, ref, lambda rng, n: ([rng.randrange(hi) for _ in range(n)], [rng.randrange(hi) for _ in range(rng.randrange(0, n + 3))]), SIZES_L, TEST_L, [([], []), ([1], []), ([BIG], [1]), ([5, 3, 9], [2, 8, 8, 1])])


def fam_group(idx):
    r = _rng("group", idx); kind = r.choice(["rle", "hist", "longest", "distinct_runs", "runlens"])
    lo = r.choice([2, 3, 5])
    if kind == "rle": return _mk(f"gen_group_{idx:05d}", "Output the run-length encoding as one flat list [v1, c1, v2, c2, ...]: each maximal run of equal consecutive elements contributes its value then its length.", L, L, lambda xs: [z for k, g in __import__("itertools").groupby(xs) for z in (k, len(list(g)))], lambda rng, n: [rng.randrange(lo) for _ in range(n)], SIZES_L, TEST_L, EDGE_L)
    if kind == "hist": return _mk(f"gen_group_{idx:05d}", f"Every element is in 0..{lo * 2 - 1}. Output a list of {lo * 2} counts: entry v is how many times v occurs.", L, L, lambda xs: [xs.count(v) for v in range(lo * 2)], lambda rng, n: [rng.randrange(lo * 2) for _ in range(n)], SIZES_L, TEST_L, [[], [0], [lo * 2 - 1, lo * 2 - 1]], pre=lambda xs: all(0 <= v < lo * 2 for v in xs))
    if kind == "longest": return _mk(f"gen_group_{idx:05d}", "Output the length of the longest run of equal consecutive elements (0 for an empty list).", L, u24, lambda xs: max((len(list(g)) for _, g in __import__("itertools").groupby(xs)), default=0), lambda rng, n: [rng.randrange(lo) for _ in range(n)], SIZES_L, TEST_L, EDGE_L)
    if kind == "distinct_runs": return _mk(f"gen_group_{idx:05d}", "Output the number of maximal runs of equal consecutive elements.", L, u24, lambda xs: len(list(__import__("itertools").groupby(xs))), lambda rng, n: [rng.randrange(lo) for _ in range(n)], SIZES_L, TEST_L, EDGE_L)
    return _mk(f"gen_group_{idx:05d}", "Output the list of lengths of the maximal runs of equal consecutive elements, in order.", L, L, lambda xs: [len(list(g)) for _, g in __import__("itertools").groupby(xs)], lambda rng, n: [rng.randrange(lo) for _ in range(n)], SIZES_L, TEST_L, EDGE_L)


TRIP = list_of(tup(u24, u24, u24))


def _cands(rng, n):
    return [(u, v, rng.randrange(1001)) for u, v in {tuple(sorted(rng.sample(range(n), 2))) for _ in range(min(3 * n, n * (n - 1) // 2 if n > 1 else 0))}] if n > 1 else []


def _uf(n, pairs):
    par = list(range(n))
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for u, v in pairs:
        a, b = find(u), find(v)
        if a != b: par[min(a, b)] = max(a, b)
    return [find(i) for i in range(n)]


def fam_recon_count(idx):
    r = _rng("recon_count", idx); tau = r.choice([300, 500, 700, 900]); kind = r.choice(["count", "sum", "maxs", "ids", "topk"]); k = r.choice([1, 2, 3])
    inp = tup(u24, L_TRIP := TRIP)
    acc = lambda p: [t for t in p[1] if t[2] >= tau]
    if kind == "count": d, out, f = f"Input is (n, cands): cands is a list of (u, v, score) with u < v < n and score in 0..1000. Output how many candidates have score >= {tau}.", u24, lambda p: len(acc(p))
    elif kind == "sum": d, out, f = f"Input is (n, cands): cands is a list of (u, v, score) with u < v < n and score in 0..1000. Output the sum of the scores of the candidates with score >= {tau}.", u24, lambda p: sum(t[2] for t in acc(p))
    elif kind == "maxs": d, out, f = f"Input is (n, cands): cands is a list of (u, v, score) with u < v < n and score in 0..1000. Output the number of distinct nodes that appear in a candidate with score >= {tau}.", u24, lambda p: len({x for t in acc(p) for x in t[:2]})
    elif kind == "ids": d, out, f = f"Input is (n, cands): cands is a list of (u, v, score) with u < v < n and score in 0..1000. Output the list of (u, v) of the candidates with score >= {tau}, in input order.", list_of(tup(u24, u24)), lambda p: [(t[0], t[1]) for t in acc(p)]
    else: d, out, f = f"Input is (n, cands): cands is a list of (u, v, score) with u < v < n and score in 0..1000. Consider the candidates with score >= {tau}; output the {k} with the highest score as (u, v, score), ordered by descending score then ascending u then ascending v (fewer if fewer qualify).", TRIP, lambda p: sorted(acc(p), key=lambda t: (-t[2], t[0], t[1]))[:k]
    return _mk(f"gen_recon_count_{idx:05d}", d, inp, out, f, lambda rng, n: (n, _cands(rng, n)), range(0, 10), [72, 144], [(0, []), (2, [(0, 1, 1000)]), (3, [(0, 1, 500), (1, 2, 500)])])


def fam_recon_uf(idx):
    r = _rng("recon_uf", idx); tau = r.choice([300, 500, 700, 900]); kind = r.choice(["count", "largest", "canon", "single", "ge2"])
    base = f"Input is (n, cands): cands is a list of (u, v, score) with u < v < n and score in 0..1000. Accept the candidates with score >= {tau} and merge their endpoints transitively into clusters (nodes 0..n-1 start as singletons). "
    lab = lambda p: _uf(p[0], [(t[0], t[1]) for t in p[1] if t[2] >= tau])
    if kind == "count": d, out, f = base + "Output the number of clusters.", u24, lambda p: len(set(lab(p)))
    elif kind == "largest": d, out, f = base + "Output the size of the largest cluster (0 when n = 0).", u24, lambda p: max(__import__("collections").Counter(lab(p)).values(), default=0)
    elif kind == "canon": d, out, f = base + "Output, for every node 0..n-1, the largest node id in its cluster.", L, lab
    elif kind == "single": d, out, f = base + "Output the number of clusters of size 1.", u24, lambda p: sum(1 for c in __import__("collections").Counter(lab(p)).values() if c == 1)
    else: d, out, f = base + "Output the number of clusters with at least 2 nodes.", u24, lambda p: sum(1 for c in __import__("collections").Counter(lab(p)).values() if c >= 2)
    return _mk(f"gen_recon_uf_{idx:05d}", d, tup(u24, TRIP), out, f, lambda rng, n: (n, _cands(rng, n)), range(0, 10), [72, 144], [(0, []), (2, [(0, 1, 1000)]), (3, [(0, 1, 500), (1, 2, 500)])])


FAMILIES = {"pipeline": fam_pipeline, "reduce": fam_reduce, "scan": fam_scan, "position": fam_position, "sortlike": fam_sortlike,
            "arith": fam_arith, "rangefn": fam_rangefn, "treefold": fam_treefold, "zip2": fam_zip2, "group": fam_group,
            "treemap": fam_treemap, "treetrav": fam_treetrav, "recon_count": fam_recon_count, "recon_uf": fam_recon_uf}


def task(family: str, idx: int) -> Program:
    return FAMILIES[family](idx)


def sample(families, n_per_family, start=0):
    return [task(f, i) for f in families for i in range(start, start + n_per_family)]
