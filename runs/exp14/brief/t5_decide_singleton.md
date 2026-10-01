# Contract: t5_decide_singleton

Input is (tau, probs): tau is an integer 0..1000 and probs a list of exactly 6 integers 0..1000, the per-mille probabilities of verbs 0..5 (probs[i] belongs to verb i; the sum is usually 1000 but may be less). Order the verb indices by descending probability, ties to the lower index first. Take the shortest non-empty prefix of this order whose probability sum is >= tau (the whole order if no prefix reaches tau): the prediction set. If the prediction set has exactly one verb, output that verb's index; otherwise output 6 (abstain). Equivalently: if max(probs) >= tau, output the lowest index i with probs[i] == max(probs), else output 6.

Input type: `tuple[u24, list[u24]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `u24`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `(900, [950, 50, 0, 0, 0, 0])` -> `0`
- `(900, [500, 500, 0, 0, 0, 0])` -> `6`
- `(0, [0, 0, 0, 0, 0, 0])` -> `0`
- `(0, [0, 0, 7, 0, 7, 0])` -> `2`
- `(166, [166, 166, 166, 166, 166, 166])` -> `0`
- `(1000, [0, 0, 0, 0, 0, 1000])` -> `5`
- `(1000, [0, 0, 0, 0, 0, 999])` -> `6`
- `(600, [100, 300, 600, 0, 0, 0])` -> `2`
