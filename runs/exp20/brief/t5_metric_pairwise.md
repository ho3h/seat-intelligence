# Contract: t5_metric_pairwise

Pairwise clustering confusion counts. Input is (pred, truth), two label lists of the same length n (node i has predicted label pred[i] and true label truth[i]); labels are arbitrary numbers and only equality matters. Over all unordered node pairs i < j: tp counts pairs with pred[i] == pred[j] and truth[i] == truth[j]; fp counts pairs with pred equal but truth different; fn counts pairs with truth equal but pred different. Output the tuple (tp, fp, fn), each mod 2^24.

Input type: `tuple[list[u24], list[u24]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `tuple[u24, u24, u24]`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `([], [])` -> `(0, 0, 0)`
- `([5], [9])` -> `(0, 0, 0)`
- `([1, 1], [1, 1])` -> `(1, 0, 0)`
- `([0, 1], [1, 1])` -> `(0, 0, 1)`
- `([1, 1], [0, 1])` -> `(0, 1, 0)`
- `([2, 2, 2, 3], [1, 1, 3, 3])` -> `(1, 2, 1)`
- `([7, 7, 8, 8, 8], [0, 1, 0, 1, 1])` -> `(1, 3, 3)`
- `([0, 1, 2], [0, 1, 2])` -> `(0, 0, 0)`
