# Contract: t5_decide_top_k

Input is (k, cands): k >= 0 and cands is a list of candidate triples (u, v, score): u, v are node ids with u < v, score an integer 0..1000 (per-mille match confidence); the same pair may occur more than once. Sort all triples (no threshold) by descending score, ties broken by ascending u, then ascending v (repeats kept, identical triples adjacent). Output the first k triples of that order, or all of them if there are fewer than k. k = 0 gives [].

Input type: `tuple[u24, list[tuple[u24, u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `list[tuple[u24, u24, u24]]`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `(0, [])` -> `[]`
- `(3, [])` -> `[]`
- `(0, [(0, 1, 5)])` -> `[]`
- `(1, [(0, 2, 5), (0, 1, 5)])` -> `[(0, 1, 5)]`
- `(2, [(1, 2, 3), (0, 1, 3), (0, 2, 9)])` -> `[(0, 2, 9), (0, 1, 3)]`
- `(9, [(0, 1, 1), (0, 1, 1), (0, 1, 2)])` -> `[(0, 1, 2), (0, 1, 1), (0, 1, 1)]`
