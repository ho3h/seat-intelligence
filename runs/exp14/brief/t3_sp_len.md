# Contract: t3_sp_len

Input is (n, s, t, edges) with s < n and t < n. The graph is UNDIRECTED: n is the number of vertices, numbered 0..n-1, and edges is a list of undirected edges (u, v) with u < n, v < n and u != v; each edge appears exactly once, in either orientation ((u, v) and (v, u) denote the same edge and never both appear), there are no self loops, and the order of the list is arbitrary. Output the length (number of edges) of a shortest path between s and t; 0 if s == t; 16777215 if s and t are in different connected components.

Input type: `tuple[u24, u24, u24, list[tuple[u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [1, 2, 3, 4, 5, 6, 7, 8]; the hidden suite also uses larger inputs (sizes [64, 128]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `(1, 0, 0, [])` -> `0`
- `(2, 0, 0, [])` -> `0`
- `(2, 0, 1, [])` -> `16777215`
- `(2, 1, 0, [])` -> `16777215`
- `(2, 1, 1, [])` -> `0`
- `(2, 0, 0, [(0, 1)])` -> `0`
- `(2, 0, 1, [(0, 1)])` -> `1`
- `(2, 1, 0, [(0, 1)])` -> `1`
