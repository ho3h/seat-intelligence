# Contract: t5_metric_rand

Rand agreement count. Input is (pred, truth), two label lists of the same length n (node i has predicted label pred[i] and true label truth[i]); labels are arbitrary numbers and only equality matters. Over all unordered node pairs i < j, a pair agrees if (pred[i] == pred[j]) equals (truth[i] == truth[j]), i.e. both put the pair together or both keep it apart. Output the number of agreeing pairs mod 2^24.

Input type: `tuple[list[u24], list[u24]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `([], [])` -> `0`
- `([5], [9])` -> `0`
- `([1, 1], [1, 1])` -> `1`
- `([0, 1], [1, 1])` -> `0`
- `([1, 1], [0, 1])` -> `0`
- `([2, 2, 2, 3], [1, 1, 3, 3])` -> `3`
- `([7, 7, 8, 8, 8], [0, 1, 0, 1, 1])` -> `4`
- `([0, 1, 2], [0, 1, 2])` -> `3`
