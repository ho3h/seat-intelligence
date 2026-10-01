# Contract: t3_cc_label

Input is (n, edges). The graph is UNDIRECTED: n is the number of vertices, numbered 0..n-1, and edges is a list of undirected edges (u, v) with u < n, v < n and u != v; each edge appears exactly once, in either orientation ((u, v) and (v, u) denote the same edge and never both appear), there are no self loops, and the order of the list is arbitrary. Output a list of length n whose entry v is the smallest vertex id in the connected component containing v (an isolated vertex is labelled with itself). n = 0 gives [].

Input type: `tuple[u24, list[tuple[u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `list[u24]`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8]; the hidden suite also uses larger inputs (sizes [64, 128]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `(0, [])` -> `[]`
- `(1, [])` -> `[0]`
- `(2, [])` -> `[0, 1]`
- `(2, [(0, 1)])` -> `[0, 0]`
- `(2, [(1, 0)])` -> `[0, 0]`
- `(3, [(2, 1)])` -> `[0, 1, 1]`
- `(4, [(0, 1), (1, 2), (2, 3)])` -> `[0, 0, 0, 0]`
- `(4, [(3, 2), (1, 2), (0, 1), (0, 3)])` -> `[0, 0, 0, 0]`
