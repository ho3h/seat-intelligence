# Contract: t5_rewrite_collapsed

Number of edges collapsed by the rewrite. Input is (c, edges). A clustering c is a list of length n (nodes are 0..n-1) where c[i] is the canonical id of node i's cluster: nodes i and j are in the same cluster iff c[i] == c[j], and a cluster's canonical id is its largest node id (so c[i] >= i and c[c[i]] == c[i]). Edges are undirected pairs (u, v) with u, v < n in either order; self loops (u == v) and repeated edges may occur. Rewriting maps edge (u, v) to (min(c[u], c[v]), max(c[u], c[v])), drops it if c[u] == c[v] (self loop), and collapses duplicates, so the rewritten graph is a set of pairs (x, y) with x < y. Output len(edges) minus the number of distinct rewritten pairs, i.e. how many input edges disappear as self loops or duplicates.

Input type: `tuple[list[u24], list[tuple[u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `([], [])` -> `0`
- `([0], [])` -> `0`
- `([0], [(0, 0)])` -> `1`
- `([0, 1], [(0, 1)])` -> `0`
- `([0, 1], [(1, 0), (0, 1), (1, 0)])` -> `2`
- `([1, 1], [(0, 1), (1, 0)])` -> `2`
- `([1, 1, 2, 3], [(0, 2), (1, 2), (3, 0), (2, 3), (3, 3)])` -> `2`
- `([2, 2, 2, 4, 4], [(0, 3), (1, 4), (2, 0), (4, 1), (3, 4)])` -> `4`
