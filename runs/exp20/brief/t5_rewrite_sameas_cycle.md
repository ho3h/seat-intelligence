# Contract: t5_rewrite_sameas_cycle

SAME_AS cycle detection. Input is a pointer list p of length n with every p[i] < n; p[i] == i means node i is a root (a self pointer is not a cycle), otherwise i points to p[i]. Output 1 if following pointers from some node never reaches a root (the pointers contain a cycle of two or more distinct nodes), else 0. [] gives 0.

Input type: `list[u24]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `[]` -> `0`
- `[0]` -> `0`
- `[1, 0]` -> `1`
- `[1, 1]` -> `0`
- `[1, 2, 0]` -> `1`
- `[1, 2, 2]` -> `0`
- `[0, 2, 3, 1]` -> `1`
- `[0, 0, 3, 4, 3]` -> `1`
