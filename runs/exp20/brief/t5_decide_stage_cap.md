# Contract: t5_decide_stage_cap

Input is (tau, cap, cands): tau is an integer threshold 0..1000, cap >= 0 the maximum number of pairs staged per run, and cands is a list of candidate triples (u, v, score): u, v are node ids with u < v, score an integer 0..1000 (per-mille match confidence); the same pair may occur more than once. The accepted triples (score >= tau) are put in processing order: descending score, ties broken by ascending u, then ascending v (repeats kept, each occurrence is its own item). The first cap accepted triples in that order are staged; the remaining accepted ones are deferred. Output (staged, deferred): staged is the list of the staged pairs (u, v) (scores dropped) in processing order, deferred the number of accepted triples not staged (0 if at most cap are accepted).

Input type: `tuple[u24, u24, list[tuple[u24, u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `tuple[list[tuple[u24, u24]], u24]`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `(500, 3, [])` -> `([], 0)`
- `(500, 0, [(0, 1, 600)])` -> `([], 1)`
- `(500, 5, [(0, 1, 600), (1, 2, 400)])` -> `([(0, 1)], 0)`
- `(100, 2, [(1, 2, 300), (0, 3, 300), (0, 2, 300), (0, 1, 50)])` -> `([(0, 2), (0, 3)], 1)`
- `(0, 1, [(0, 1, 0), (0, 1, 0)])` -> `([(0, 1)], 1)`
- `(700, 2, [(2, 3, 800), (0, 1, 900), (1, 3, 700), (0, 2, 1000)])` -> `([(0, 2), (0, 1)], 2)`
