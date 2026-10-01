# Contract: t5_rewrite_sameas_roots

SAME_AS pointer resolution. Input is a pointer list p of length n with every p[i] < n; p[i] == i means node i is a root, otherwise i points to p[i]. The pointers are acyclic: following p from any node reaches a root after finitely many steps. Output a list of length n whose entry i is the root reached from i (i itself if i is a root). Pointers need not go to larger ids and chains may be long.

Input type: `list[u24]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `list[u24]`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `[]` -> `[]`
- `[0]` -> `[0]`
- `[1, 1]` -> `[1, 1]`
- `[0, 0]` -> `[0, 0]`
- `[1, 2, 2]` -> `[2, 2, 2]`
- `[0, 0, 1, 2]` -> `[0, 0, 0, 0]`
- `[3, 3, 1, 3]` -> `[3, 3, 3, 3]`
- `[4, 0, 1, 2, 4]` -> `[4, 4, 4, 4, 4]`
