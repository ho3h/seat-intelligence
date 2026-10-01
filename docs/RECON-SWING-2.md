# RECON-SWING-2: native nets for the order-dependent T5 kernels (2026-09-30)

Question: RECON-SWING (`docs/RECON-SWING.md`) left out the 7 T5 programs that had no accepted native net. Six are
the ordered must-not-link (MNL) greedy and its pipelines, and one is the majority property table. Can they be
written as correct native nets, and how shallow can they be?

Method: one Opus-class author, hand-written HVM2, about 3 hours, nothing searched or learned.
`runs/exp18/build.py` builds the nets from `genome/lib/graphprims.py` plus new templates in `runs/exp18/lib_ext.py`
(docstrings give ports, cost and design). Verification used the unmodified `genome.verify.verify` with 2 workers
(`runs/exp18/v.py`). Nets are in `runs/exp18/<prog>.hvm`, and snapshots of each core version are in
`runs/exp18/v1|v3|v5/`. Logs are `verify_v1.log`, `verify_v3.log` and `verify_v5.log`.

## Results

Every net passes the hidden suite on seeds 0, 1 and 2. Metrics are the verifier's seed-0 medians over the big cases
(n = 72, 144). "Bend" is the frozen author's accepted B1 net (`runs/g1/b1/seed0/<prog>/state.json`, `best`).

| program | seeds 0-2 | **depth / itrs (v5, final)** | v1 depth / itrs | Bend depth / itrs | depth vs Bend | itrs vs Bend |
| --- | --- | --- | --- | --- | --- | --- |
| t5_conflict_greedy | pass | **5,629 / 5,642,227** | 10,297 / 5,400,478 | 392,335 / 13,085,162 | 70x shallower | 2.3x fewer |
| t5_conflict_greedy_cap | pass | **6,411 / 6,486,379** | 12,245 / 6,417,228 | 1,024,563 / 9,801,570 | 160x | 1.5x fewer |
| t5_conflict_skipped | pass | **5,969 / 3,870,472** | 10,721 / 3,743,551 | 2,824,226 / 20,425,482 | 473x | 5.3x fewer |
| t5_reconcile_canon_mnl | pass | **2,320 / 1,467,610** | 3,780 / 1,654,235 | 51,774 / 4,779,874 | 22x | 3.3x fewer |
| t5_prop_merged | pass | **1,683 / 334,758** | same net | 24,199 / 1,748,640 | 14x | 5.2x fewer |
| t5_reconcile_full | pass | **7,079 / 3,846,638** | 12,211 / 3,762,091 | 1,357,814 / 10,632,752 | 192x | 2.8x fewer |
| t5_reconcile_full_props | pass | **5,788 / 4,732,237** | 10,413 / 5,330,327 | none accepted | n/a | n/a |

All seven now have an accepted-quality native net: 21 of 21 verifier runs pass (`runs/exp18/verify_v5.log`; the v1
and v3 snapshots also pass 21 of 21 each). Seeds 1 and 2 give v5 medians of 2,727-5,194 (greedy kernels) and
1,735-1,758 (prop_merged). Weak spot: the small (authoring-size) cases cost 56-74k interactions against Bend's 5-14k
(fixed cost of the 1,024-bucket score trie; prop_merged has no such trie and is 4-8k).

## Design

### The ordered greedy (6 programs share one core)

The spec's greedy is sequential, and this design keeps it sequential. It makes one decision per accepted candidate,
in (score desc, u, v) order, and makes each decision cheap in depth. I measured the previous agent's proposal (run
the greedy only inside clusters that contain an MNL pair) on the verifier's big cases (`runs/exp18/analyze.py`). It
does not pay on this distribution:

- Unconstrained components usually form one giant conflicted component that holds 90-99% of the accepted edges
  (for example 222 of 232, or 138 of 139).
- The filter would save little on the median and would add an LP pass of about 1,000 depth.

It stays a valid refinement for sparse real data such as OpenSanctions (27 conflicted clusters). Greedy clusters
refine the unconstrained components, and a component with no MNL pair inside (and size <= cap) needs no ordered
processing.

**Sort** (`sort_scores`). Candidates stream once (about 2.3 rounds each) into a depth-10 trie keyed by `1000 - score`.
Each bucket is an ascending list of packed keys `(u << L) | v`, kept by a sorted-insert act. Candidates below tau are
dropped by the act: the reject bit rides in the payload, so no switch sits on the stream's chain. Buckets hold only
ties, so they stay tiny. A left-to-right fold over the 1,024 buckets threads the greedy state through the sorted
candidates.

Duplicate candidates in the pipeline kernels are not removed. They are harmless:

- a pair that was skipped is skipped again, because clusters only grow and the cap only tightens;
- a pair that was merged is a no-op.

**State.** The state has four parts:

- a node trie (depth L), whose leaf is `(label, cluster size)`, with label = largest member;
- two numeric copies of the node trie, used for pre-expanded keyed gets;
- an MNL trie (depth lg|mnl|), whose leaf is the current labels of the pair's two ends;
- the skipped-pair list, threaded as a difference list.

**One candidate (v3).**

1. A pre-expanded get reads the labels and sizes of u and v, then a scalar relabel applies the pending decision.
2. `(A, B)` and the pending decision are broadcast down the MNL trie. Each leaf relabels its ends and tests
   `{la, lb} == {A, B}`. The flags are OR-reduced back up the trie.
3. The decision uses inline switches.
   - A == B, or sA + sB > cap, resolves to the no-op before the reduction arrives.
   - Otherwise it gives `(min, max, sA + sB)` or the no-op.
4. The node trie is relabelled one candidate late (x == lo -> hi; sz := S for x in {lo, hi}). This is off the
   critical path, and only its copies feed later gets.

**v5 (final): speculating on the late bit.** A decision has two parts:

- an early part `E_k = (lo, hi, S)`, the merge candidate k would do, known as soon as A_k and B_k are;
- a late bit `ok_k`, meaning no MNL conflict, known only after the reduction.

Round k evaluates candidate k under both hypotheses for ok_{k-1}: the MNL leaves test on the "after k-2" labels
and on those labels relabelled by E_{k-1}, and pack the two flags as `c0 + 2*c1` into one OR-reduction. The root
selects with ok_{k-1} through a 3-round switch. The node trie lags two candidates.

**Edge rewrite** (`edge_rewrite`, reconcile_full*):

- Endpoint lookups are multicast requests. Reply wires are registered while the edge list streams, then delivered
  from the final label trie in O(L).
- `(min, max)` is pushed into bucket `min` with a sorted, dedup insert. Self loops are dropped by the act.
- A fold emits the buckets in key order.

**Property table** (`prop_merge`, prop_merged and full_props):

- The cluster of each attribute comes from the same multicast lookup.
- Its value is count-inserted into bucket `(cid << 2) | key`, a depth L+2 trie of ascending `(value, count)` lists.
- A fold emits `(cid, key, majority)` in key order. The majority is a scan that keeps the first strictly larger
  count, so ties go to the smallest value.
- prop_merged gets n by counting list `c`, which is DUP-copied: one copy is counted and the other is written into
  a trie by position-keyed `set`s. This is `list_to_trie`.

## Where the depth goes (measured, `runs/exp18/slope.py`, `probe.py`)

`slope.py` takes the first k candidates of the n = 144 seed-0 case. Its slopes are in rounds per candidate:

| core | with 55 MNL pairs | no MNL pairs | median depth, greedy seed 0 |
| --- | --- | --- | --- |
| v1: one traversal per candidate: conflict flags up, relabel down | ~58 | ~38 | 10,297 |
| v2: + label lookahead, same-cluster shortcut (REF switches) | ~58 | ~38 | 8,675 |
| v3: separate MNL trie, node trie off the chain, inline switches | ~49 | ~26 | 6,815 |
| v4: v3 + relabel of the ends inside the MNL leaves | ~49 (no change) | ~26 | n/a |
| v5: v3 + speculation on ok_{k-1} | ~40 | ~28 | 5,629 |

The fixed part of the depth is about 170-400: lg, tries, the sort stream and output. The rest is the per-candidate
chain times m (m = accepted candidates, 50-290 here).

The micro-benchmarks set the constants:

| operation | rounds |
| --- | --- |
| one OPR with a waiting operand | 2 |
| one DUP level | 1 |
| inline switch select | about 6 (switch, eq, and one round per context nesting level) |
| switch whose branch is a REF with an 11-deep context | about 11 |

What held the chain at about 40:

- the decision itself: compare, select min/max, the pre-conflict gate, and a hypothesis select, about 20 rounds;
- the MNL trie round trip: broadcast lg M, leaf test about 8, reduction 2 lg M.

v4 showed that moving work around the root does not help. Only removing a dependency does, as v5 did.

## What limited me, and the next step

- **Sequential by specification.** The greedy needs m decisions in order, so depth is Theta(m * per-step). Per-step
  fell from 58 to 40, and I think 15-20 is reachable:
  - speculate two candidates deep (the 2^2 hypotheses fit in a 4-bit flag of one reduction);
  - replace OPR chains in the decision with precomputed tables;
  - use a sparse, balanced trie of the MNL pairs that are relevant (both ends in one unconstrained component).
- **A deeper change would batch candidates.** A window of w candidates whose clusters are pairwise disjoint is
  independent and can be decided in one round. With a conflict matrix over the window's 2w cluster labels
  (16 bits for w = 2) reduced in one pass, the root simulates w steps. This amortises the broadcast and reduction.
- **Small inputs.** Fixed cost is 55-70k interactions against Bend's 5-14k. The 1,024-bucket score trie dominates it;
  a sparse score trie or a composite-key sort would remove it.
- **Work.** Work is O(m * (2^L + |mnl|)) interactions (about 5M at n = 144), about half of Bend's.
- **Scale.** At G4 scale with long clusters, the filter to conflicted components plus per-component parallel greedies
  is the route. Here one giant component made it moot.
