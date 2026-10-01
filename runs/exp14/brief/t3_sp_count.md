# Contract: t3_sp_count

Input is (n, s, t, edges) with s < n and t < n. The graph is DIRECTED: n is the number of vertices, numbered 0..n-1, and edges is a list of directed edges (u, v) meaning an edge from u to v, with u < n, v < n and u != v; no ordered pair appears twice (u->v and v->u may both be present), there are no self loops, and the order of the list is arbitrary. Let D be the minimum number of edges on a directed path from s to t. Output the number of distinct directed paths from s to t that have exactly D edges (two paths are distinct if their vertex sequences differ), reduced mod 2^24. If s == t the answer is 1 (the empty path). If t is not reachable from s the answer is 0.

Input type: `tuple[u24, u24, u24, list[tuple[u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [1, 2, 3, 4, 5, 6, 7, 8]; the hidden suite also uses larger inputs (sizes [64, 128]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `(1, 0, 0, [])` -> `1`
- `(2, 0, 0, [])` -> `1`
- `(2, 0, 1, [])` -> `0`
- `(2, 1, 0, [])` -> `0`
- `(2, 1, 1, [])` -> `1`
- `(2, 0, 0, [(0, 1)])` -> `1`
- `(2, 0, 1, [(0, 1)])` -> `1`
- `(2, 1, 0, [(0, 1)])` -> `0`
