# Contract: t5_decide_drop_known

Input is (known, cands): known is a list of already existing SAME_AS pairs (a, b) with a < b (any order, repeats possible) and cands is a list of candidate triples (u, v, score): u, v are node ids with u < v, score an integer 0..1000 (per-mille match confidence); the same pair may occur more than once. Output the triples of cands whose pair (u, v) is not equal to any known pair (exact match of both ids, (u, v) == (a, b); only direct pairs count, not pairs implied transitively), unchanged and in original order, repeats kept. No score threshold is applied.

Input type: `tuple[list[tuple[u24, u24]], list[tuple[u24, u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `list[tuple[u24, u24, u24]]`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `([], [])` -> `[]`
- `([(0, 1)], [])` -> `[]`
- `([], [(0, 1, 9)])` -> `[(0, 1, 9)]`
- `([(0, 1)], [(0, 1, 900), (1, 2, 800), (0, 1, 100)])` -> `[(1, 2, 800)]`
- `([(0, 1), (1, 2)], [(0, 2, 999), (1, 2, 5)])` -> `[(0, 2, 999)]`
- `([(2, 3), (2, 3)], [(0, 3, 1), (2, 3, 2), (0, 2, 3)])` -> `[(0, 3, 1), (0, 2, 3)]`
