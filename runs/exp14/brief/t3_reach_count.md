# Contract: t3_reach_count

Input is (n, s, edges) with s < n (so n >= 1). The graph is DIRECTED: n is the number of vertices, numbered 0..n-1, and edges is a list of directed edges (u, v) meaning an edge from u to v, with u < n, v < n and u != v; no ordered pair appears twice (u->v and v->u may both be present), there are no self loops, and the order of the list is arbitrary. Output the number of distinct vertices v such that there is a directed path (following edges forward) from s to v; s itself always counts (path of length 0), so the result is between 1 and n.

Input type: `tuple[u24, u24, list[tuple[u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [1, 2, 3, 4, 5, 6, 7, 8]; the hidden suite also uses larger inputs (sizes [64, 128]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `(1, 0, [])` -> `1`
- `(2, 0, [])` -> `1`
- `(2, 1, [])` -> `1`
- `(2, 0, [(0, 1)])` -> `2`
- `(2, 1, [(0, 1)])` -> `1`
- `(2, 0, [(1, 0)])` -> `1`
- `(2, 1, [(1, 0)])` -> `2`
- `(2, 0, [(0, 1), (1, 0)])` -> `2`
