# GRAPH-LIB: is the graph vocabulary real and reusable? (exp8, 2026-09-30)

Question: GRAPH-SWING (`docs/GRAPH-SWING.md`, `runs/exp5`) hand-wrote 8 shallow T3 nets from a few reusable ideas.
Are those ideas a real vocabulary? That is, can new, correct, low-depth programs be made quickly by composing them?

What was done:

1. The exp5 templates became a documented, unit-tested library, `genome/lib/graphprims.py`.
2. 8 new programs were composed from it: every t3_a program where the frozen author's native net lost to Bend, and
   that exp5 had not already done.
3. Each program was verified with the unmodified `genome.verify.verify` on seeds 0, 1 and 2 (3 workers).

The code that builds the nets is `runs/exp8/build.py`; the nets are in `runs/exp8/<prog>.hvm`; the table comes from
`runs/exp8/results.py`, which writes `runs/exp8/results.json`.

## The library (`genome/lib/graphprims.py`)

Each primitive is a Python function. It adds HVM2 definitions to a `Book` and returns the name of its entry
definition. A program is a list of primitive calls plus glue:

- the `@prog` root;
- the walker's `step` and `fin` bodies;
- small leaf bodies, written as HVM text.

A `Book` deduplicates shared helpers and rejects name clashes. All tries are complete binary tries of depth `L`,
keyed by vertex id with the high bit first. `L = lg(n-1)`. Keys `>= 2^L` alias, so glue must guard them.

A signature is the tree that the entry REF must meet.

Key to the tables:

- **exp5**: the template came from exp5.
- **gen**: generalised from exp5.
- **v1**: new before any program was composed.
- **v2**: added while composing the 8 programs.

Depth and interaction figures are rough, taken from the unit tests and the nets.

**Tries, lookups and walkers**

| primitive | signature | computes | cost | origin |
| --- | --- | --- | --- | --- |
| `lg` | `(x L)` | number of bits of x | ~4 rounds/bit | exp5 |
| `const_trie(leaf)` | `(L t)` | every leaf = a closed term (`0`, `16777215`, `(0 *)`, `(y y)`) | ~2L rounds, ~3 itrs/node | exp5 |
| `iota_trie` | `(L (base t))` | leaf i = base+i | ~3L rounds | exp5 |
| `update(act)` | `(t (k (L (P t2))))` | leaf k := act(leaf, P). Control depends only on k and L, so the update expands before t exists; a chain of updates collapses in O(L) once keys are known | ~16 rounds/level, ~12 itrs/level | exp5 (`nav`) |
| acts | `ACTS[...]` | set1, set, inc, add, or, min, max, push (adjacency lists), reply (multicast); v2: dec, peek (DUP copy of the leaf out through P) | | exp5 + v2 |
| `get` | `(t (k (L o)))` | read leaf k; the rest is erased | ~12 rounds/level | v1 |
| `stream(K, step, fin)` | `@p_blk ~ (list (S0 out))` | blocked speculative list walker: K cells matched ahead, one SWI per cell, and Nil erases the overrun | ~2.3 rounds/cell at K=16 | exp5 |
| `adjacency` | `(G (u (L ((v w) G2))))` | push (v w) onto u's list; `gl_zl` is the empty trie | as update | exp5 |

**Traversals**

| primitive | signature | computes | cost | origin |
| --- | --- | --- | --- | --- |
| `reduce(leaf, op, idx, env)` | `(t (L [(base] [(E] o)))` | op in `+ \| & max min` over the leaf map `leaf(x[, i][, E])` | ~3-5 rounds/level | gen (`cnt`/`pairs`/`cf`/`ccn`) |
| `fold(leaf)` | `(t (L (base (E (acc o)))))` | accumulator threaded right to left through the leaves, which run in parallel | ~4 rounds/level | gen (`tl`) |
| `to_list` | `(t (L (0 (n (tail o)))))` | first n leaves as a list; an instance of fold | | exp5 (`tl`) |
| `filter_list(pred, emit)` | `(t (L (0 (E (tail o)))))` | index or value of every leaf where pred holds, in key order | | v1 |
| `scatter(upd, key)` | `(t (L (0 ((Lh E) (H H2)))))` | each leaf does a keyed update into another trie (histogram, inverse map) | | v1 |
| `zip2(leaf)` | `(a (c (L o)))` | leafwise combination of two tries | ~3 rounds/level | v1 |
| `zip2e(leaf)` | `(a (c (L (E o))))` | zip2 with an environment; runs a sub-computation (a whole frontier loop) at every leaf of an outer trie, all in parallel | | **v2** |
| `bcast(upd)` | `(T (Lo ((Li (k P)) T2)))` | the same inner update applied to every sub-trie under an outer trie (replicates data per batch) | 2^Lo updates | **v2** |
| `mapreduce(leaf, op)` | `(t (L (base (E (t2 o)))))` | a reduce that also rebuilds the trie, so the trie is not consumed | as reduce | **v2** |
| `POP24` | leaf-body snippet | 24-bit popcount (SWAR) | 18 OPRs | **v2** |

**Multicast and loops**

| primitive | signature | computes | cost | origin |
| --- | --- | --- | --- | --- |
| `mc_empty` / `mc_request` | `(L q)` / `(q (k (L (r q2))))` | request trie; registers the reply wire r at key k (wires as return addresses) | as update | exp5 (`zq`/`pu`) |
| `mc_deliver` | `(v (q L))` | wires value leaf k into chain k; every reply wire gets a DUP copy | O(L) rounds, pure wiring | exp5 (`zmq`) |
| `mc_deliver_keep` | `(v (q (L v2)))` | the same, keeping a leafwise copy of v. This is the safe way to use a numeric trie twice | | **v2** |
| `frontier(act, msg, comb, ident)` | `@p_loop ~ ((G (D (C (L X)))) Dfinal)` | generic frontier fixpoint. Each round is one traversal of (adjacency, state, messages). A leaf runs `act` (new state, flag, message base); flagged leaves send `msg` along their out-list into the next round's trie, combined by `comb`. The loop stops when no flag is set | ~75-155 rounds per round | gen (exp5 `sssp_core`) |
| `relax(maximize)` / `sssp` | frontier instances | min-plus relaxation with a budget (SSSP, min-label components); max-label propagation with 0/1 edge enables; single-source seed | | exp5 / v1 |
| `iterate(body)` | `@p_it ~ (S Sfinal)` | sequential while loop over any state | ~3 rounds/iteration of overhead | **v2** |

**Unit tests** (`python3 -m genome.lib.test_graphprims`): 29 tests, 29 pass.

- Each primitive is wrapped in a tiny `@prog`, linted with the verifier's static check, run by the pinned executor,
  and compared with a Python model on random and edge inputs.
- Every act, reduce op, filter, scatter, multicast, sssp and max-label propagation is covered, and so is every v2
  primitive.
- The tests found one library bug: `RELAX_MAX` left one wire dangling. The executor tolerated it, but the verifier's
  lint rejected the net. Since then the unit tests run the same lint.

**Abstraction tax.** exp5's hand-written `t3_cc_count` was rebuilt purely from the library
(`runs/exp8/extra_t3_cc_count.hvm`):

- depth 1,536, against 1,536 for the hand-written net;
- 260,695 interactions, against 256,254 (+1.7%).

Composition costs nothing measurable.

## The 8 new programs (t3_a)

Selection: every t3_a program (excluding the four that exp5 already did) whose earlier native net was worse than its
Bend net by depth, ranked by depth ratio. States were combined as in `genome/exp_quick.py`. Only 5 of the 8 are
"much worse" (5x-25x): topo_order, cc_largest, cyclic_vertices, closure_size and two_colour. degrees (2.0x),
reach_queries (1.9x) and bipartite_comps (1.2x) complete the list because t3_a has no other losers. The six t3_a
programs with no accepted native net at all were not attempted.

Metrics are the verifier's medians over the large cases at seed 0, as in GRAPH-SWING. "prev" is the frozen author's
best accepted native net and "Bend" is the same author's accepted B1 net. "Authoring lines" counts the program's
build function plus every shared glue string it uses, so shared glue is counted again for each program. It is set
against the size of the emitted net.

| program | seeds 0-2 | authoring lines / net lines | new primitives needed | prev native depth / itrs | Bend depth / itrs | **composed depth / itrs** | depth vs Bend | itrs, Bend / composed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| t3_topo_order | pass | 46 / 211 | mapreduce, iterate, acts dec + peek | 7,612,236 / 39,148,799 | 299,627 / 1,468,975 | **35,987 / 1,275,025** | 8.3x shallower | 1.15 |
| t3_cc_largest | pass | 29 / 214 | none | 1,530,976 / 3,658,652 | 70,099 / 1,493,869 | **2,783 / 537,149** | 25x | 2.78 |
| t3_cyclic_vertices | pass | 60 / 219 | bcast, zip2e | 5,492,966 / 11,018,715 | 349,790 / 3,766,260 | **2,088 / 1,658,224** | 168x | 2.27 |
| t3_closure_size | pass | 62 / 240 | (bcast, zip2e reused) + POP24 | 115,390 / 13,712,984 | 12,550 / 7,164,360 | **4,089 / 1,198,412** | 3.1x | 5.98 |
| t3_two_colour | pass | 52 / 260 | mc_deliver_keep | 1,494,285 / 5,677,989 | 300,279 / 840,255 | **3,910 / 563,954** | 77x | 1.49 |
| t3_degrees | pass | 19 / 82 | none | 4,856 / 333,204 | 2,473 / 72,267 | **464 / 69,287** | 5.3x | 1.04 |
| t3_reach_queries | pass | 61 / 265 | (bcast, zip2e reused) | 81,167 / 5,557,647 | 43,347 / 6,464,579 | **2,263 / 1,094,045** | 19x | 5.91 |
| t3_bipartite_comps | pass | 52 / 260 | (mc_deliver_keep reused) | 618,516 / 1,597,445 | 522,124 / 1,208,119 | **3,713 / 592,059** | 141x | 2.04 |

Depth: all 8 composed nets are shallower than both the earlier native net and Bend: 3.1x to 168x shallower than Bend,
median about 22x. Interactions: fewer than Bend on 8 of 8 (1.04x to 6x fewer) and fewer than the earlier native net
on 8 of 8. Every net passed seed 0 at its first verification and then passed seeds 1 and 2. None needed debugging at
the program level, and the only failure was the library bug above.

**How each was composed** (the algorithmic idea is the author's; the parts are library words):

- **cc_largest**: min-label `relax` → `scatter` histogram (add at key label[i]) → `reduce` max.
- **degrees**: `stream` + `update(inc)` ×2 per edge → `to_list`.
- **two_colour / bipartite_comps**:
  - `frontier` with the library's `RELAX` act on d = 2·label + parity, message d^1, seeded from `zip2(iota, iota)` = 2i.
  - A component is bipartite iff no edge has d[u] = d[v] at the fixpoint. This is checked by per-edge
    `mc_request` / `mc_deliver_keep` lookups plus `update(or)`, keyed by u (two_colour) or by the component root
    (bipartite_comps).
  - Outputs: two_colour is a `fold` emitting `(d&1) | bad·INF`; bipartite_comps is `zip2` + an indexed `reduce`.
- **cyclic_vertices / closure_size / reach_queries**: batched reachability, where each batch of 24 sources shares one
  24-bit mask.
  - `bcast` replicates the adjacency trie per batch, while `update(or)` seeds each source's bit at its
    out-neighbours, so reach needs at least one step.
  - `zip2e` runs one OR-`frontier` per batch, all batches in parallel.
  - Outputs:
    - cyclic_vertices: an indexed `reduce` of "own bit set";
    - closure_size: `POP24` minus the own bit;
    - reach_queries: `mc_request` / `mc_deliver` lookups written into the output through a list-with-hole walker
      state.
- **topo_order**: the lexicographically smallest topological order is sequential by nature (Kahn with a min-heap).
  `iterate` runs one step per output vertex:
  1. `mapreduce` finds the min index with in-degree 0 and keeps the in-degree trie;
  2. `update` removes that vertex;
  3. `update(peek)` copies its out-list;
  4. `stream` walks the out-list, decrementing in-degrees.

  It costs about 280 rounds per vertex, still 8x shallower than Bend.

**Extras.** These were built before the coordinator restricted this experiment to t3_a, because other agents own
t3_b and t5. They are kept as evidence. All pass seeds 0-2, and all compose from v1 with no new primitive (v1 was
designed with these seven contracts in view, so they are not a blind test):

| program | authoring / net lines | prev native depth | Bend depth / itrs | composed depth / itrs |
| --- | --- | --- | --- | --- |
| t5_cluster_label | 25 / 179 | 14,790,343 | 133,009 / 822,264 | **1,977 / 364,500** (67x) |
| t5_reconcile_canon | 29 / 181 | 16,618,753 | 167,825 / 1,083,329 | **3,336 / 573,578** (50x) |
| t5_cluster_members_of | 24 / 202 | 390,305 | 12,979 / 27,440 | **617 / 142,097** (21x shallower, 5.2x more itrs) |
| t3_wsp_dist | 29 / 202 | 1,039,936 | 77,513 / 479,781 | **1,752 / 233,495** (44x) |
| t5_prop_conflict_keys | 57 / 180 | 46,930,173 | 25,377 / 917,965 | **1,255 / 308,120** (20x) |
| t5_rewrite_neighbours | 44 / 175 | 10,017,141 | 269,291 / 1,247,038 | **1,384 / 235,468** (195x) |
| t3_kcore_size | 44 / 185 | 624,405 | 55,423 / 1,650,287 | **1,383 / 199,347** (40x) |

## Honest accounting

- **Blind or not.** Library v1 (frozen copy: `runs/exp8/graphprims_v1_frozen.py`) was designed after reading the 7
  extra contracts, so those 7 are not a blind test. The 8 t3_a programs were chosen after v1 was frozen, because the
  coordinator changed the target set. That makes them a real held-out test, with these results:
  - 2 of 8 composed from v1 alone (cc_largest, degrees);
  - 2 of 8 needed one new primitive (two_colour, bipartite_comps);
  - 3 of 8 needed two new primitives (the reachability family);
  - 1 of 8 needed two new primitives and two acts (topo_order).
  - In total, 5 new primitives (mc_deliver_keep, zip2e, bcast, mapreduce, iterate), 2 acts (dec, peek) and 1 leaf
    snippet (POP24). Every addition was reused, or is generic.
- **Effort.** By file timestamps, v1 was frozen at 03:28 and the last t3_a net was built at 03:36, so 7 programs
  plus the 5 new primitives took under 15 minutes of wall time; the v2 unit tests followed. That works out to
  roughly 4:1 emitted-net lines per authoring line. Most of the authoring lines are still raw HVM glue
  (walker step bodies, the `@prog` root, leaf bodies), not bare primitive calls.
- **Baseline caveat.** "Bend" in these tables is the frozen author's B1 net. BEND-FAIR-BASELINE
  (`docs/BEND-FAIR-BASELINE.md`, exp7) found that about 2/3 of the exp5 gap, on a log scale, was algorithmic: a
  strong Bend author using the same ideas came within 1.4-3.2x of native. The 3-195x ratios here therefore measure
  library plus algorithm against a weak Bend author, not the medium on its own.
- **Where the wins come from.**
  - The big depth wins come from the same few ideas as exp5: keyed updates that expand early, tries instead of scans,
    frontier rounds, and multicast.
  - The weak spots are the same as well. Frontier rounds cost about 75-155 depth each, so long chains are
    rounds-bound (worst cases 5k-21k).
  - Fixed overheads make small, sparse inputs cost more interactions than Bend in some cases (members_of).
  - k synchronous rounds (walk_count, cheapest_k_walk) would compose on `frontier` but would not beat Bend on depth.

## How much of T3/T5 is composable? (judgement from the contracts)

The 100 T3+T5 programs were classified as follows:

- **done**: composed or hand-built from these parts;
- **A**: composable from the v2 library plus glue;
- **B**: needs about one more generic primitive;
- **C**: the core algorithm is outside this vocabulary.

| class | T3 (50) | T5 (50) |
| --- | --- | --- |
| done (23) | 18: exp5's 8, these 8, wsp_dist, kcore_size | 5: cluster_label, reconcile_canon, cluster_members_of, prop_conflict_keys, rewrite_neighbours |
| A (46) | 19: reach_count, bfs_dist, sp_len, sp_count, khop, cc_label, cycle_rank, tree_parents, apsp_matrix, eccentricities, wiener_index, max_degree_vertex, greedy_coloring, minimax_path, euler_start, count_shortest_paths, lex_shortest_path, walk_count*, cheapest_k_walk* | 27: decide_filter, decide_count, decide_singleton, cluster_canon/count/sizes/histogram/largest/singletons/list/emit/closure_pairs/implied_unproposed/canon_of/same/merge_count/count_ge, conflict_count/pairs/flags, prop_conflicts, rewrite_edges/weighted/collapsed/degrees/sameas_roots/sameas_cycle |
| B (17) | 5: bfs_order (rank/compaction), scc_count + scc_label (fold across the outer batch level), girth, forest_mis (dataflow DP with end-reduction, exp5's `zx`) | 12: decide_normalise/drop_known/order/top_k/stage_cap/stage_idem, prop_majority/merged/distinct_per_key, metric_pairwise/purity/rand. All need one missing word: a **sparse keyed trie / sort over arbitrary 24-bit keys** |
| C (14) | 8: bridges, articulation, articulation_points, msf_weight, mst_second, bipartite_matching, max_flow, clique_number | 6: conflict_greedy, conflict_greedy_cap, conflict_skipped, reconcile_canon_mnl, reconcile_full, reconcile_full_props (sequential constrained greedy merges) |

\* composable, but k synchronous frontier rounds would lose to Bend on depth.

In total, about 69% are composable now (done + A), and about 86% with about 5 more primitives: a sparse trie/sort,
rank/compaction, an outer-level fold, dataflow end-reduction, and word-bitset rows. That gives a library of about 30
primitives. The last 14% need other algorithms (DFS low-link, flow or matching, Borůvka, sequential greedy, NP-hard
search), and the library would supply only parts of them.

## Weak-author probe (haiku, library plus docs only)

A Claude Haiku subagent was given PHYSICS.md, this document, the library, `runs/exp8/build.py` and the unit tests as
examples. It was asked to compose 4 class-A t3_a programs it had not seen before: bfs_dist, khop, cycle_rank and
tree_parents. None had an accepted native net, apart from bfs_dist. The budget was 8 verification attempts each and
about 40 minutes. Its builder and nets are in `runs/exp8/weak/`; every status below was re-checked independently.

| program | attempts | seeds 0-2 | seed-0 depth / itrs | Bend depth / itrs |
| --- | --- | --- | --- | --- |
| t3_bfs_dist | 1 | **pass** | 817 / 100,701 | 2,884,372 / 14,601,729 (3,500x shallower) |
| t3_khop | 2 | seed 0 pass, seed 1 fail | 822 / 134,219 | no accepted Bend metrics |
| t3_cycle_rank | 5 | reject (it gave up; stub `@prog`) | - | 218,269 / 1,470,499 |
| t3_tree_parents | 5 | reject (a wire used once) | - | 38,833 / 1,675,848 |

- **What worked.** With the library, a much weaker model got a correct net that is 3,500x shallower than Bend at its
  first attempt, on the program closest to a worked example (sssp + to_list).
- **What failed.** The failures were all in the glue, not in the primitives:
  - linearity mistakes: unused wires, and values needed twice without a DUP;
  - an unfinished `@prog` for m - n + c;
  - a trap in the contract. khop with k = 16777215 counts unreachable vertices (their distance 16777215 <= k), and
    the haiku net counted only reachable ones.
- **Reading.** The vocabulary lowers the skill needed for programs that are one primitive chain away from an example.
  It does not remove the need to write correct linear glue, or to choose the algorithm. A glue-level linter or
  typed combinators (`Book` checking linearity per body, and named tuple ports in place of positional
  `(a (b c))` trees) is the obvious next word.

## Verdict

- **Is the vocabulary real and reusable?** Yes.
  - The parts are real: 29 of 29 unit tests pass, and the abstraction tax is 0% on depth and +1.7% on interactions.
  - The parts are reusable: 15 of 15 composed programs pass seeds 0-2 at their first verification.
  - The results are low-depth: every composed net beats the earlier native net and Bend on depth, by 3.1x to 195x
    over Bend.
  - On held-out contracts the library needed about 0.6 new primitives per program, and the additions were reused
    right away.
- **Does "the vocabulary makes authors need less skill" hold up?** Only partly, and not shown here.
  - The library clearly removes the error-prone wiring skill: port conventions, linearity, bracket balance, and the
    keyed-update and loop templates. The one net-level bug came from inside the library, and composition added none.
  - The wins, however, came from algorithmic moves the library does not supply, all made by an Opus-class author who
    also wrote the library:
    - parity packed into the label (d = 2·label + parity);
    - 24 sources batched per mask, with `bcast` replication;
    - seeding at out-neighbours for "at least one step";
    - Kahn written as `iterate` over a `mapreduce`;
    - noticing that decide + cluster only needs "max score ≥ tau".
  - A weaker author (Haiku) given the library passed 1 of 4 new programs on all seeds (plus 1 on seed 0 only).
    It failed on glue linearity and on algorithm choice, which are exactly the parts the library leaves to the
    author. So the vocabulary reduces the skill needed, but does not remove it.
