# Contract: t5_conflict_count

Input is (c, mnl). A clustering c is a list of length n (nodes are 0..n-1) where c[i] is the canonical id of node i's cluster: nodes i and j are in the same cluster iff c[i] == c[j], and a cluster's canonical id is its largest node id (so c[i] >= i and c[c[i]] == c[i]). Must-not-link pairs are (a, b) with a < b < n, no pair listed twice, in arbitrary order. A must-not-link pair (a, b) is violated when c[a] == c[b]. Output the number of violated must-not-link pairs.

Input type: `tuple[list[u24], list[tuple[u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `([], [])` -> `0`
- `([0], [])` -> `0`
- `([1, 1], [(0, 1)])` -> `1`
- `([0, 1], [(0, 1)])` -> `0`
- `([2, 2, 2, 3], [(0, 3), (1, 2), (0, 1)])` -> `2`
- `([1, 1, 3, 3], [(2, 3), (0, 2)])` -> `1`
- `([4, 4, 4, 4, 4], [(3, 4), (0, 1), (1, 4), (2, 3)])` -> `4`
