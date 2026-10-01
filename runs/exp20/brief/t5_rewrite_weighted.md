# Contract: t5_rewrite_weighted

Weighted edge rewrite. Input is (c, edges) with edges as triples (u, v, w). A clustering c is a list of length n (nodes are 0..n-1) where c[i] is the canonical id of node i's cluster: nodes i and j are in the same cluster iff c[i] == c[j], and a cluster's canonical id is its largest node id (so c[i] >= i and c[c[i]] == c[i]). Edges are undirected with u, v < n in either order and an integer weight w; self loops and repeated edges may occur. Each edge maps to (min(c[u], c[v]), max(c[u], c[v])); edges with c[u] == c[v] are dropped together with their weight. Output one triple (x, y, total) per distinct rewritten pair, where total is the sum mod 2^24 of the weights of all edges mapped to (x, y) (a total may be 0), sorted ascending lexicographically (by first component, then second, then third).

Input type: `tuple[list[u24], list[tuple[u24, u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `list[tuple[u24, u24, u24]]`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `([], [])` -> `[]`
- `([0], [(0, 0, 5)])` -> `[]`
- `([0, 1], [(0, 1, 3), (1, 0, 4)])` -> `[(0, 1, 7)]`
- `([0, 1], [(0, 1, 0)])` -> `[(0, 1, 0)]`
- `([1, 1, 2], [(0, 2, 1), (2, 1, 2), (1, 0, 50)])` -> `[(1, 2, 3)]`
- `([0, 1], [(0, 1, 16777215), (1, 0, 2)])` -> `[(0, 1, 1)]`
- `([2, 2, 2, 4, 4], [(0, 3, 1), (1, 4, 2), (2, 0, 3), (4, 1, 4), (3, 4, 5)])` -> `[(2, 4, 7)]`
