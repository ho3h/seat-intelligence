"""T1 Arithmetic and lists (30 programs). All arithmetic is mod 2^24 unless stated."""
from . import program
from ..types import u24, list_of, tup, MASK

L = list_of(u24)
M = MASK
BIG = MASK  # 16777215


def rl(rng, n, hi=1000):            # random list of length n
    return [rng.randrange(hi) for _ in range(n)]


def rl_wide(rng, n):
    return [rng.randrange(M + 1) for _ in range(n)]


S = list(range(0, 17))              # authoring size parameters for list programs
LE = [[], [0], [BIG], [1, 1, 1]]    # common list edge cases

program("t1_sum", "T1", "Sum of all elements, mod 2^24. Empty list gives 0.",
        L, u24, lambda xs: sum(xs) & M, lambda r, n: rl_wide(r, n), S, edges=LE + [[BIG, 1], [BIG, BIG]])

program("t1_product", "T1", "Product of all elements, mod 2^24. Empty list gives 1.",
        L, u24, lambda xs: __import__("math").prod(xs) & M, lambda r, n: rl(r, n, 50), S,
        edges=LE + [[0, 5], [4096, 4096], [BIG, BIG]])

program("t1_length", "T1", "Number of elements in the list.",
        L, u24, len, lambda r, n: rl(r, n), S, edges=LE)

program("t1_max", "T1", "Largest element. Empty list gives 0.",
        L, u24, lambda xs: max(xs, default=0), lambda r, n: rl_wide(r, n), S, edges=LE + [[3, 9, 9, 1]])

program("t1_min", "T1", "Smallest element. Empty list gives 16777215.",
        L, u24, lambda xs: min(xs, default=BIG), lambda r, n: rl_wide(r, n), S, edges=LE + [[3, 0, 9]])

program("t1_count_even", "T1", "Number of even elements.",
        L, u24, lambda xs: sum(1 for x in xs if x % 2 == 0), lambda r, n: rl(r, n), S, edges=LE + [[2, 4, 6], [1, 3]])

program("t1_map_double", "T1", "Every element multiplied by 2, mod 2^24, same order.",
        L, L, lambda xs: [(2 * x) & M for x in xs], lambda r, n: rl_wide(r, n), S, edges=LE + [[8388608, 8388607]])

program("t1_map_inc", "T1", "Every element plus 1, mod 2^24 (16777215 wraps to 0), same order.",
        L, L, lambda xs: [(x + 1) & M for x in xs], lambda r, n: rl_wide(r, n), S, edges=LE)

program("t1_filter_even", "T1", "The even elements, in original order.",
        L, L, lambda xs: [x for x in xs if x % 2 == 0], lambda r, n: rl(r, n), S, edges=LE + [[1, 3, 5], [2, 4]])

program("t1_filter_gt", "T1", "Input is (k, xs). The elements of xs strictly greater than k, in original order.",
        tup(u24, L), L, lambda a: [x for x in a[1] if x > a[0]],
        lambda r, n: (r.randrange(1000), rl(r, n)), S, edges=[(0, []), (5, [5, 6, 4]), (BIG, [BIG])])

program("t1_reverse", "T1", "The list in reverse order.",
        L, L, lambda xs: xs[::-1], lambda r, n: rl(r, n), S, edges=LE + [[1, 2, 3]])

program("t1_append", "T1", "Input is (xs, ys). All of xs followed by all of ys.",
        tup(L, L), L, lambda a: a[0] + a[1],
        lambda r, n: (rl(r, n // 2), rl(r, n - n // 2)), S, edges=[([], []), ([1], []), ([], [2]), ([1, 2], [3])])

program("t1_take", "T1", "Input is (k, xs). The first k elements of xs (all of xs if it has fewer than k).",
        tup(u24, L), L, lambda a: a[1][:a[0]],
        lambda r, n: (r.randrange(0, n + 3), rl(r, n)), S, edges=[(0, [1, 2]), (5, []), (2, [1, 2, 3]), (3, [1, 2, 3])])

program("t1_drop", "T1", "Input is (k, xs). xs without its first k elements (empty if it has k or fewer).",
        tup(u24, L), L, lambda a: a[1][a[0]:],
        lambda r, n: (r.randrange(0, n + 3), rl(r, n)), S, edges=[(0, [1, 2]), (5, []), (2, [1, 2, 3]), (3, [1, 2, 3])])

program("t1_last", "T1", "The last element. Empty list gives 0.",
        L, u24, lambda xs: xs[-1] if xs else 0, lambda r, n: rl(r, n), S, edges=LE)

program("t1_nth", "T1", "Input is (i, xs). xs[i], counting from 0. Out of range gives 0.",
        tup(u24, L), u24, lambda a: a[1][a[0]] if a[0] < len(a[1]) else 0,
        lambda r, n: (r.randrange(0, n + 3), rl(r, n)), S, edges=[(0, []), (0, [7]), (1, [7]), (2, [1, 2, 3])])

program("t1_replicate", "T1", "Input is (n, v). A list of n copies of v.",
        tup(u24, u24), L, lambda a: [a[1]] * a[0], lambda r, n: (n, r.randrange(M + 1)), S, edges=[(0, 5), (1, 0)])

program("t1_range", "T1", "Input is n. The list [0, 1, ..., n-1].",
        u24, L, lambda n: list(range(n)), lambda r, n: n, S, edges=[0, 1, 2])

program("t1_zip_add", "T1", "Input is (xs, ys). Elementwise sums mod 2^24, truncated to the shorter list.",
        tup(L, L), L, lambda a: [(x + y) & M for x, y in zip(*a)],
        lambda r, n: (rl_wide(r, n), rl_wide(r, r.randrange(0, n + 3))), S, edges=[([], []), ([1], []), ([BIG], [1])])

program("t1_dot", "T1", "Input is (xs, ys). Sum of xi*yi over the shorter length, mod 2^24.",
        tup(L, L), u24, lambda a: sum(x * y for x, y in zip(*a)) & M,
        lambda r, n: (rl(r, n), rl(r, r.randrange(0, n + 3))), S, edges=[([], []), ([4096], [4096]), ([BIG], [BIG])])

program("t1_prefix_sums", "T1", "Running totals: output[i] = xs[0]+...+xs[i], mod 2^24. Same length as input.",
        L, L, lambda xs: [sum(xs[:i + 1]) & M for i in range(len(xs))], lambda r, n: rl_wide(r, n), S, edges=LE)

def _fact(n):
    r = 1
    for i in range(2, n + 1): r = (r * i) & M
    return r
program("t1_factorial", "T1", "Input is n. n! mod 2^24.",
        u24, u24, _fact, lambda r, n: n, list(range(0, 21)), test_sizes=[100, 320], edges=[0, 1, 2, 12, 13])

def _fib(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, (a + b) & M
    return a
program("t1_fibonacci", "T1", "Input is n. The n-th Fibonacci number (F0=0, F1=1), mod 2^24.",
        u24, u24, _fib, lambda r, n: n, list(range(0, 31)), test_sizes=[250, 480], edges=[0, 1, 2, 35, 36])

def _gcd(a):
    x, y = a
    while y: x, y = y, x % y
    return x
program("t1_gcd", "T1", "Input is (a, b). The greatest common divisor. gcd(a, 0) = a, gcd(0, 0) = 0.",
        tup(u24, u24), u24, _gcd, lambda r, n: (r.randrange(0, 2 ** n), r.randrange(0, 2 ** n)), list(range(1, 17)),
        test_sizes=[18, 22], edges=[(0, 0), (0, 7), (7, 0), (12, 18), (17, 17), (BIG, BIG - 1)])

def _powmod(a):
    b, e, m = a
    r, b = 1 % m, b % m
    while e:
        if e & 1: r = r * b % m
        b = b * b % m; e >>= 1
    return r
program("t1_powmod", "T1", "Input is (base, exp, m) with 1 <= m <= 4096. base^exp mod m (0^0 = 1 mod m).",
        tup(u24, u24, u24), u24, _powmod,
        lambda r, n: (r.randrange(0, 2 ** 16), r.randrange(0, 2 ** n), r.randrange(1, 4097)), list(range(1, 13)),
        test_sizes=[16, 20], edges=[(0, 0, 1), (0, 0, 7), (2, 10, 1000), (5, 0, 4096), (4095, 4095, 4096)])

program("t1_popcount", "T1", "Input is n. The number of 1 bits in the binary representation of n.",
        u24, u24, lambda n: bin(n).count("1"), lambda r, n: r.randrange(0, 2 ** n), list(range(1, 17)),
        test_sizes=[20, 24], edges=[0, 1, BIG, 8388608, 255])

def _collatz(n):
    c = 0
    while n > 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        c += 1
    return c
program("t1_collatz", "T1", "Input is n >= 1. Number of Collatz steps (n/2 if even, else 3n+1) until n reaches 1.",
        u24, u24, _collatz, lambda r, n: r.randrange(1, 2 ** n), list(range(1, 11)),
        test_sizes=[14, 17], edges=[1, 2, 3, 27, 97])

# big numbers: little-endian lists of base-4096 digits, no trailing zero digits; zero is []
B = 4096
def _to_int(ds): return sum(d * B ** i for i, d in enumerate(ds))
def _from_int(v):
    ds = []
    while v: ds.append(v % B); v //= B
    return ds
def _bn(r, n):  # random bignum with n digits (top digit nonzero)
    ds = [r.randrange(B) for _ in range(n)]
    if ds and ds[-1] == 0: ds[-1] = 1 + r.randrange(B - 1)
    return ds

program("t1_bignum_add", "T1",
        "Input is (a, b), each a natural number as a little-endian list of base-4096 digits (each digit 0..4095) "
        "with no trailing zero digits; zero is []. Output the sum in the same form.",
        tup(L, L), L, lambda a: _from_int(_to_int(a[0]) + _to_int(a[1])),
        lambda r, n: (_bn(r, n), _bn(r, r.randrange(0, n + 1))), list(range(0, 13)),
        edges=[([], []), ([4095], [1]), ([4095, 4095], [1]), ([1], [4095, 4095, 4095])])

program("t1_bignum_mul_small", "T1",
        "Input is (a, k): a is a natural number in the little-endian base-4096 form of bignum_add "
        "(no trailing zero digits; zero is []) and k is a plain number 0..4095. Output a*k in the same bignum form.",
        tup(L, u24), L, lambda a: _from_int(_to_int(a[0]) * a[1]),
        lambda r, n: (_bn(r, n), r.randrange(B)), list(range(0, 13)),
        edges=[([], 5), ([1], 0), ([4095, 4095], 4095), ([4095] * 5, 4095)])

program("t1_bignum_mul", "T1",
        "Input is (a, b), natural numbers in the little-endian base-4096 form of bignum_add. Output a*b in that form.",
        tup(L, L), L, lambda a: _from_int(_to_int(a[0]) * _to_int(a[1])),
        lambda r, n: (_bn(r, n), _bn(r, r.randrange(0, n + 1))), list(range(0, 9)),
        edges=[([], []), ([], [1]), ([4095], [4095]), ([4095] * 4, [4095] * 4)])
