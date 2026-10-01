# Contract: t5_decide_stage_idem

Input is (ledger, proposals). ledger is a list of existing staging entries (verb, target, status): verb 0..5, target a node id, status 0 = Staged, 1 = Applied, 2 = Rejected, 3 = Undone; the same (verb, target) may appear several times with different statuses. proposals is a list of (verb, target). Process the proposals in order. A proposal is dropped if the ledger has at least one entry with the same verb, the same target and status 0 or 1 (Rejected and Undone entries never block), or if an identical (verb, target) proposal was already kept earlier in this list; otherwise it is kept. The same target with a different verb does not block. Output the kept proposals (verb, target) in their original order.

Input type: `tuple[list[tuple[u24, u24, u24]], list[tuple[u24, u24]]]`  (encoded as in PHYSICS.md: tuples right-nested, lists as (0 *) / (1 (head tail)))
Output type: `list[tuple[u24, u24]]`

Input sizes: authoring sizes n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; the hidden suite also uses larger inputs (sizes [72, 144]) and an exhaustive sweep of tiny inputs.

Examples (input -> expected output):

- `([], [])` -> `[]`
- `([], [(0, 1), (0, 1), (1, 1)])` -> `[(0, 1), (1, 1)]`
- `([(0, 1, 0)], [(0, 1), (1, 1)])` -> `[(1, 1)]`
- `([(0, 1, 1)], [(0, 1)])` -> `[]`
- `([(0, 1, 2), (3, 4, 3)], [(0, 1), (3, 4), (3, 4)])` -> `[(0, 1), (3, 4)]`
- `([(2, 5, 3), (2, 5, 1)], [(2, 5), (2, 6)])` -> `[(2, 6)]`
- `([(5, 0, 0)], [])` -> `[]`
