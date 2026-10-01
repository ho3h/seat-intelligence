# Contract: t5_decide_normalise

Input is cands, a list of candidate triples (u, v, score) with u != v and score an integer 0..1000; a pair may appear in either orientation (u < v or u > v) and more than once. Normalise each triple's pair to (min(u, v), max(u, v)). Collapse all triples with the same normalised pair into one triple carrying the highest score among them (ties: the first occurrence in input order is kept, which has the same score, so the output is unaffected). Output one triple (u, v, score) per distinct normalised pair, with u < v, sorted by ascending u, then ascending v. Empty input gives [].

Input type: `list[tuple[u24, u24, u24]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `list[tuple[u24, u24, u24]]`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `[]` -> `[]`
- `[(3, 1, 40)]` -> `[(1, 3, 40)]`
- `[(1, 3, 40), (3, 1, 90), (1, 3, 60)]` -> `[(1, 3, 90)]`
- `[(2, 0, 5), (0, 2, 5), (0, 1, 7)]` -> `[(0, 1, 7), (0, 2, 5)]`
- `[(5, 4, 0), (4, 5, 1000), (0, 9, 300), (9, 0, 300)]` -> `[(0, 9, 300), (4, 5, 1000)]`
