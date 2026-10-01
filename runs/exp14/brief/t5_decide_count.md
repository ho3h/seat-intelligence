# Contract: t5_decide_count

Input is (tau, cands): tau is an integer threshold 0..1000 and cands is a list of candidate triples (u, v, score): u, v are node ids with u < v, score an integer 0..1000 (per-mille match confidence); the same pair may occur more than once. Output the number of triples with score >= tau (every occurrence of a repeated pair counts). Empty cands gives 0.

Input type: `tuple[u24, list[tuple[u24, u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `(500, [])` -> `0`
- `(0, [(0, 1, 0)])` -> `1`
- `(1000, [(0, 1, 999), (1, 2, 1000)])` -> `1`
- `(500, [(0, 1, 500), (0, 2, 499), (1, 2, 501)])` -> `2`
- `(600, [(2, 3, 700), (0, 1, 700), (2, 3, 650), (0, 1, 700), (1, 3, 100)])` -> `4`
- `(1000, [(0, 1, 1000), (0, 1, 1000)])` -> `2`
