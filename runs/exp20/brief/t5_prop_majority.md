# Contract: t5_prop_majority

Majority merge of one property. Input is (k, key, c, attrs) with key in 0..3. A clustering c is a list of length n (nodes are 0..n-1) where c[i] is the canonical id of node i's cluster: nodes i and j are in the same cluster iff c[i] == c[j], and a cluster's canonical id is its largest node id (so c[i] >= i and c[c[i]] == c[i]). Attributes are triples (node, key, value) with node < n, key in 0..3, any value; each (node, key) occurs at most once; list order is arbitrary. A node may lack some keys. The cluster is the set of nodes i with c[i] == k (possibly empty if k is not a canonical id). The merged value of a key in a cluster is the value carried by the most attribute triples of that key among the cluster's nodes; ties go to the smallest value. Output the merged value of `key` in that cluster, or 16777215 if no node of the cluster has that key.

Input type: `tuple[u24, u24, list[u24], list[tuple[u24, u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `(0, 0, [], [])` -> `16777215`
- `(0, 0, [0], [])` -> `16777215`
- `(0, 3, [0], [(0, 3, 7)])` -> `7`
- `(1, 0, [1, 1], [(1, 0, 4), (0, 0, 5)])` -> `4`
- `(2, 1, [2, 2, 2], [(0, 1, 9), (1, 1, 3), (2, 1, 9), (2, 0, 1)])` -> `9`
- `(2, 2, [2, 2, 2], [(0, 1, 9)])` -> `16777215`
- `(1, 0, [0, 1, 2], [(0, 0, 1), (1, 0, 2), (2, 0, 3)])` -> `2`
- `(5, 0, [0, 1], [(0, 0, 1)])` -> `16777215`
