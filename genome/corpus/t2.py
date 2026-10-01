"""T2 Sorting and search (30 programs)."""
from collections import Counter
from . import program
from ..types import u24, list_of, tup, MASK

L = list_of(u24)
M = MASK
BIG = MASK
S = list(range(0, 17))
LE = [[], [0], [BIG], [2, 2, 2], [3, 1, 2]]
PAIR = list_of(tup(u24, u24))


def rl(rng, n, hi=100):
    return [rng.randrange(hi) for _ in range(n)]

def rls(rng, n, hi=100):
    return sorted(rl(rng, n, hi))

def rlu(rng, n):  # strictly increasing
    return sorted(rng.sample(range(0, max(4 * n, 8)), n))


program("t2_sort", "T2", "The elements in ascending order (duplicates kept).",
        L, L, sorted, lambda r, n: rl(r, n, 1000), S, edges=LE + [[5, 4, 3, 2, 1], [1, 2, 3], [BIG, 0, BIG]])

program("t2_sort_desc", "T2", "The elements in descending order (duplicates kept).",
        L, L, lambda xs: sorted(xs, reverse=True), lambda r, n: rl(r, n, 1000), S, edges=LE)

program("t2_sort_pairs", "T2",
        "Input is a list of (key, value) pairs. The pairs ordered by ascending key; pairs with equal keys keep their original relative order (stable).",
        PAIR, PAIR, lambda ps: sorted(ps, key=lambda p: p[0]),
        lambda r, n: [(r.randrange(8), r.randrange(1000)) for _ in range(n)], S,
        edges=[[], [(1, 2)], [(1, 5), (1, 4), (0, 9)]])

program("t2_merge", "T2", "Input is (xs, ys), both sorted ascending. One sorted ascending list of all their elements.",
        tup(L, L), L, lambda a: sorted(a[0] + a[1]), lambda r, n: (rls(r, n // 2), rls(r, n - n // 2)), S,
        edges=[([], []), ([1], []), ([], [2]), ([1, 3], [2, 4]), ([1, 1], [1])])

program("t2_is_sorted", "T2", "1 if the list is in non-decreasing order, else 0. Empty and single-element lists give 1.",
        L, u24, lambda xs: int(all(a <= b for a, b in zip(xs, xs[1:]))),
        lambda r, n: rls(r, n, 20) if r.random() < 0.5 else rl(r, n, 20), S, edges=LE + [[1, 2, 2, 3], [1, 3, 2]])

def _bsearch(a):
    xs, t = a
    for i, x in enumerate(xs):
        if x == t: return i
    return BIG
program("t2_search", "T2",
        "Input is (xs, t) with xs sorted ascending, no duplicates. The index of t in xs, or 16777215 if absent.",
        tup(L, u24), u24, _bsearch,
        lambda r, n: (lambda xs: (xs, r.choice(xs) if xs and r.random() < 0.6 else r.randrange(0, 4 * n + 8)))(rlu(r, n)), S,
        edges=[([], 3), ([5], 5), ([5], 4), ([1, 3, 5], 1), ([1, 3, 5], 5), ([1, 3, 5], 2)])

program("t2_lower_bound", "T2", "Input is (xs, t) with xs sorted ascending. The number of elements strictly less than t.",
        tup(L, u24), u24, lambda a: sum(1 for x in a[0] if x < a[1]),
        lambda r, n: (rls(r, n, 30), r.randrange(0, 34)), S, edges=[([], 3), ([1, 1, 1], 1), ([1, 1, 1], 2)])

program("t2_upper_bound", "T2", "Input is (xs, t) with xs sorted ascending. The number of elements less than or equal to t.",
        tup(L, u24), u24, lambda a: sum(1 for x in a[0] if x <= a[1]),
        lambda r, n: (rls(r, n, 30), r.randrange(0, 34)), S, edges=[([], 3), ([1, 1, 1], 1), ([1, 1, 1], 0)])

program("t2_median", "T2", "The element at index len//2 of the sorted list (upper median for even lengths). Empty list gives 0.",
        L, u24, lambda xs: sorted(xs)[len(xs) // 2] if xs else 0, lambda r, n: rl(r, n, 1000), S, edges=LE + [[4, 1], [4, 1, 9]])

program("t2_kth_smallest", "T2",
        "Input is (k, xs), k counting from 0. The k-th smallest element (duplicates counted); 0 if k >= len(xs).",
        tup(u24, L), u24, lambda a: sorted(a[1])[a[0]] if a[0] < len(a[1]) else 0,
        lambda r, n: (r.randrange(0, n + 2), rl(r, n, 1000)), S, edges=[(0, []), (0, [9]), (1, [9]), (1, [3, 1, 2])])

program("t2_dedup_sorted", "T2", "Input is a sorted ascending list. The same list with repeated values collapsed to one.",
        L, L, lambda xs: sorted(set(xs)), lambda r, n: rls(r, n, 10), S,
        edges=[[], [0], [BIG], [2, 2, 2], [1, 1, 2, 2, 2, 3], [0, BIG, BIG]])

program("t2_distinct_count", "T2", "The number of distinct values in the list (order arbitrary).",
        L, u24, lambda xs: len(set(xs)), lambda r, n: rl(r, n, 10), S, edges=LE)

program("t2_top_k", "T2",
        "Input is (k, xs). The k largest elements in descending order (duplicates counted); all of them if len(xs) < k.",
        tup(u24, L), L, lambda a: sorted(a[1], reverse=True)[:a[0]],
        lambda r, n: (r.randrange(0, n + 2), rl(r, n, 1000)), S, edges=[(0, [1]), (3, []), (2, [1, 5, 3]), (5, [2, 2])])

program("t2_rank", "T2", "Input is (x, xs). The number of elements of xs strictly less than x.",
        tup(u24, L), u24, lambda a: sum(1 for y in a[1] if y < a[0]),
        lambda r, n: (r.randrange(0, 40), rl(r, n, 40)), S, edges=[(0, []), (5, [5, 5]), (6, [5, 5])])

program("t2_partition", "T2",
        "Input is (p, xs). A pair (lo, hi): lo holds the elements < p and hi the elements >= p, each in original order.",
        tup(u24, L), tup(L, L), lambda a: ([x for x in a[1] if x < a[0]], [x for x in a[1] if x >= a[0]]),
        lambda r, n: (r.randrange(0, 40), rl(r, n, 40)), S, edges=[(3, []), (0, [1, 2]), (BIG, [1, 2])])

program("t2_argmin", "T2", "Index of the first occurrence of the smallest element. Empty list gives 0.",
        L, u24, lambda xs: xs.index(min(xs)) if xs else 0, lambda r, n: rl(r, n, 20), S, edges=LE + [[3, 1, 1, 2]])

program("t2_argmax", "T2", "Index of the first occurrence of the largest element. Empty list gives 0.",
        L, u24, lambda xs: xs.index(max(xs)) if xs else 0, lambda r, n: rl(r, n, 20), S, edges=LE + [[3, 9, 9, 2]])

program("t2_histogram", "T2", "Every element is in 0..15. Output a list of 16 counts: entry v is how many times v occurs.",
        L, L, lambda xs: [xs.count(v) for v in range(16)], lambda r, n: rl(r, n, 16), S, edges=[[], [0], [15, 15], list(range(16))])

program("t2_merge3", "T2", "Input is (xs, ys, zs), each sorted ascending. One sorted ascending list of all elements.",
        tup(L, L, L), L, lambda a: sorted(a[0] + a[1] + a[2]),
        lambda r, n: (rls(r, n // 3), rls(r, n // 3), rls(r, n - 2 * (n // 3))), S, edges=[([], [], []), ([1], [], [0]), ([2], [2], [2])])

program("t2_sort_dedup", "T2", "The distinct values of the list in ascending order.",
        L, L, lambda xs: sorted(set(xs)), lambda r, n: rl(r, n, 12), S, edges=LE)

program("t2_second_largest", "T2", "The second element of the list sorted in descending order (duplicates counted). Fewer than 2 elements gives 0.",
        L, u24, lambda xs: sorted(xs, reverse=True)[1] if len(xs) > 1 else 0, lambda r, n: rl(r, n, 1000), S,
        edges=LE + [[5, 5], [1, 9, 9]])

def _closest(a):
    x, xs = a
    return min(xs, key=lambda e: (abs(e - x), e)) if xs else 0
program("t2_closest", "T2",
        "Input is (x, xs). The element of xs with the smallest absolute difference from x; ties go to the smaller element. Empty xs gives 0.",
        tup(u24, L), u24, _closest, lambda r, n: (r.randrange(0, 60), rl(r, n, 60)), S,
        edges=[(5, []), (5, [3, 7]), (5, [7, 3]), (0, [BIG])])

program("t2_count_in_range", "T2", "Input is (lo, hi, xs). The number of elements e with lo <= e <= hi.",
        tup(u24, u24, L), u24, lambda a: sum(1 for e in a[2] if a[0] <= e <= a[1]),
        lambda r, n: (lambda lo: (lo, lo + r.randrange(0, 30), rl(r, n, 60)))(r.randrange(0, 40)), S,
        edges=[(0, 0, []), (5, 4, [4, 5]), (5, 5, [5, 5])])

def _mode(xs):
    if not xs: return 0
    c = Counter(xs); best = max(c.values())
    return min(v for v, k in c.items() if k == best)
program("t2_mode", "T2", "The most frequent value; ties go to the smallest value. Empty list gives 0.",
        L, u24, _mode, lambda r, n: rl(r, n, 6), S, edges=LE + [[1, 2, 2, 1], [3, 3, 1]])

def _longest_run(xs):
    best = cur = 0; prev = None
    for x in xs:
        cur = cur + 1 if x == prev else 1
        prev = x; best = max(best, cur)
    return best
program("t2_longest_run", "T2", "The length of the longest run of equal consecutive elements. Empty list gives 0.",
        L, u24, _longest_run, lambda r, n: rl(r, n, 3), S, edges=LE + [[1, 1, 2, 2, 2, 1]])

def _lis(xs):
    best = []
    for i, x in enumerate(xs):
        best.append(1 + max([best[j] for j in range(i) if xs[j] < x], default=0))
    return max(best, default=0)
program("t2_lis", "T2", "The length of the longest strictly increasing subsequence (not necessarily contiguous). Empty list gives 0.",
        L, u24, _lis, lambda r, n: rl(r, n, 30), S, edges=LE + [[1, 2, 3, 4], [4, 3, 2, 1], [1, 5, 2, 6, 3, 7]])

program("t2_inversions", "T2", "The number of pairs i < j with xs[i] > xs[j].",
        L, u24, lambda xs: sum(1 for i in range(len(xs)) for j in range(i + 1, len(xs)) if xs[i] > xs[j]) & M,
        lambda r, n: rl(r, n, 50), S, edges=LE + [[3, 2, 1], [1, 2, 3]])

program("t2_merge_dedup", "T2", "Input is (xs, ys), both sorted ascending. The sorted list of distinct values occurring in either.",
        tup(L, L), L, lambda a: sorted(set(a[0]) | set(a[1])), lambda r, n: (rls(r, n // 2, 12), rls(r, n - n // 2, 12)), S,
        edges=[([], []), ([1, 1], [1]), ([1, 2], [2, 3])])

program("t2_intersect", "T2", "Input is (xs, ys), both strictly increasing. The sorted list of values in both.",
        tup(L, L), L, lambda a: sorted(set(a[0]) & set(a[1])), lambda r, n: (rlu(r, n // 2), rlu(r, n - n // 2)), S,
        edges=[([], []), ([1], []), ([1, 2, 3], [2, 3, 4]), ([1, 2], [3, 4])])

program("t2_union", "T2", "Input is (xs, ys), both strictly increasing. The strictly increasing list of values in either.",
        tup(L, L), L, lambda a: sorted(set(a[0]) | set(a[1])), lambda r, n: (rlu(r, n // 2), rlu(r, n - n // 2)), S,
        edges=[([], []), ([1], []), ([1, 2, 3], [2, 3, 4]), ([1, 2], [3, 4])])
