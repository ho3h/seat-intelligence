# Contract: t5_prop_conflicts

Property-conflict count. Input is (c, attrs). A clustering c is a list of length n (nodes are 0..n-1) where c[i] is the canonical id of node i's cluster: nodes i and j are in the same cluster iff c[i] == c[j], and a cluster's canonical id is its largest node id (so c[i] >= i and c[c[i]] == c[i]). Attributes are triples (node, key, value) with node < n, key in 0..3, any value; each (node, key) occurs at most once; list order is arbitrary. A node may lack some keys. For a cluster and a key, collect the values of that key over all nodes of the cluster; the (cluster, key) is a property conflict if it has more than one distinct value. Output the number of conflicting (cluster, key) combinations, summed over all clusters and keys.

Input type: `tuple[list[u24], list[tuple[u24, u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `([], [])` -> `0`
- `([0], [])` -> `0`
- `([0], [(0, 3, 7)])` -> `0`
- `([1, 1], [(0, 0, 5), (1, 0, 5)])` -> `0`
- `([1, 1], [(1, 0, 4), (0, 0, 5)])` -> `1`
- `([2, 2, 2], [(0, 1, 9), (1, 1, 3), (2, 1, 9), (2, 0, 1)])` -> `1`
- `([1, 1, 3, 3], [(3, 2, 6), (2, 2, 2), (0, 2, 2), (1, 3, 0), (0, 3, 0), (1, 2, 8)])` -> `2`
- `([0, 1, 2], [(0, 0, 1), (1, 0, 2), (2, 0, 3)])` -> `0`
