# GRAPH-SWING: can a strong author reverse the T3 graph loss? (2026-09-30)

Question: native nets beat Bend on list, sort and tree programs but lost on T3 graphs (median depth about 4x worse).
Is that loss in the medium, or did the frozen authors use the wrong algorithms and data structures?

Method: ranked every T3 program with an accepted native and Bend net by native/Bend depth (states combined exactly
as `genome/exp_quick.py` does). Took six of the worst plus `t3_cc_count` as an extra, and `t3_in_out_degrees`, where
native already won. Wrote new nets by hand (Opus-class author, about 2 hours) in `runs/exp5/`. `build.py` puts together
hand-written HVM2 text (`*.hvm.txt`) and two small text macros in `lib.py` (`stream`, `nav`). Nothing is searched
or learned. Every net passes the hidden suite at seed 0 and on a fresh seed 1. Metrics are the verifier's median
over the six large cases at seed 0. "prev" is the frozen author's best native net; "Bend" is the same author's
accepted B1 net.

| program | prev native depth / itrs | **new net depth / itrs** | Bend depth / itrs | new vs Bend depth |
| --- | --- | --- | --- | --- |
| t3_wsp_all_from | 8,188,482 / 15,986,071 | **371 / 60,872** | 1,483 / 184,806 | 4.0x shallower |
| t3_budget_reach | 2,217,791 / 11,631,520 | **981 / 115,529** | 9,421 / 51,142 | 9.6x shallower, 2.3x more work |
| t3_sources_sinks | 401,208 / 912,685 | **615 / 88,444** | 1,862 / 99,293 | 3.0x |
| t3_triangle_count | 187,143 / 29,108,182 | **802 / 157,680** | 2,333 / 3,454,846 | 2.9x |
| t3_line_graph_edges | 385,590 / 1,042,255 | **607 / 81,485** | 6,218 / 1,092,212 | 10x |
| t3_dag_longest | 3,020,036 / 41,138,269 | **711 / 51,330** | 49,861 / 1,579,691 | 70x |
| t3_cc_count (extra) | 3,152,664 / 14,049,361 | **1,536 / 256,254** | 164,351 / 890,296 | 107x |
| t3_in_out_degrees (already a win) | 2,077 / 184,017 | **586 / 79,143** | 4,580 / 481,209 | 7.8x |

Depth: the new net beats both the old native net and Bend on 8 of 8 programs. Interactions: it beats both on 7 of
8. The exception is budget_reach, where Bend's early-stopping Dijkstra does 51k interactions against our 116k.

## Design ideas, and what each one bought

1. **Complete binary trie keyed by vertex id, updated by keyed updates that expand before the data exists
   (`nav`).** An update's control flow (the switch on the level, the switch on the key bit) depends only on the key
   and the trie depth, so each update expands as soon as its key is known. The chain of m updates then collapses
   in O(depth) rounds, not O(m*depth). This one idea turns O(n*m) scans into O(m + log n). Measured with the
   plain one-SWI-per-cell walker (K=1): sources_sinks 401k -> 1,671, line_graph 386k -> 1,614, triangle 187k ->
   1,258, dag_longest 3.0M -> 1,414. That walker already beats Bend's depth on all four, though only by 10% on
   sources_sinks.
2. **Blocked speculative list walker (`stream`, K=16).** The walker matches K cells ahead with one nested pattern
   (2 rounds per cell), puts one SWI per cell's tag, and wires the per-cell work in a chain. It needs no
   end-of-list test: a Nil payload `*` erases everything past the end, including the unused SWIs. Walker floor:
   about 7 rounds/cell -> about 2.3. Effect: sources_sinks 1,671 -> 615 (K=4: 825, K=32: 601), line_graph 1,614 ->
   607, triangle 1,258 -> 802, dag_longest 1,414 -> 711. This trick lives in the net and Bend cannot express it:
   Bend's `match` compiles to one switch per cell.
3. **Wires as return addresses (multicast).** A request trie leaf is a DUP chain `(in out)`, and each consumer
   pushes a reply wire. At the end, row/value w is wired into chain w. Nothing is routed back.
   triangle_count uses it to fetch the two adjacency rows (16-bit word tries) for each edge, and then computes
   popcount(AND). dag_longest uses it to build the DP recursion as a dataflow net: values ripple along the DAG
   with no rounds and no global synchronisation (63-hop chain case: 1,359 depth, where Bend's rounds give 49,861).
4. **Frontier Bellman-Ford over tries (SSSP core, shared by wsp, budget, cc).** Each round is one traversal of
   (adjacency, distances, candidates). Leaves that improved emit min-updates into the next round's candidate
   trie, and the OR-reduce decides whether to continue. The budget acts as an acceptance bound, so only vertices
   within budget join the frontier.

What did **not** help:
- One round of lookahead (expanding round k+1 while round k runs) plus balanced context tuples: 0% on depth,
  +10-20% interactions (`*__lookahead.hvm`).
- Diagnosis: the per-round critical path (about 155 rounds) is the gated emission. A keyed update expands only
  after the leaf's improve-switch fires. Making emission ungated (every leaf emits every round; quiet leaves emit
  a clamped sentinel) halves the per-round depth (155 -> 74) at 2-4x the work: cc_count 1,536 -> 1,227 (worst
  case 10,014 -> 5,247), budget 981 -> 953 at 3.5x the interactions, and wsp 371 -> 564, worse because of the
  extra round (`*__ungated.hvm`). That is a pure depth-for-work trade.
- The fixed overhead is about 140-370 rounds (lg(n), building tries, one traversal per phase). It dominates on
  tiny inputs.

## Verdict

The graph loss was an author problem, not the medium. With the right data structure (a trie keyed by vertex, with
updates that expand ahead of the data) and parallel formulations (dataflow DP, frontier rounds, multicast), native
nets beat the same programs' Bend nets by 3-107x on depth, and on 7 of 8 also on interactions. On graph problems
the medium has an advantage that follows from its semantics. Where control depends only on keys, all of that
structure unfolds early and the data then streams through it. The input list is the one remaining sequential
floor, about 2 rounds per edge.

Caveats:
- The Bend baselines come from the frozen author. Ideas 1, 3 and 4 are algorithms, and a strong Bend author could
  partly port them (Bend has unscoped lambdas for idea 3). Idea 2 and the eraser-driven end detection are
  net-only; they account for a further 1.6-2.7x.
- Rounds-based algorithms (SSSP, components) still pay about 75-155 depth per round, and their worst cases
  (long chains: cc_count up to 10k) are rounds-bound.

## A systematic version: a library of parallel graph primitives

This session's primitives, as reusable net templates:
- `stream(step, fin)`: the blocked list walker.
- `nav(act)`: keyed trie update. Instances: set, inc, add, min, max, push-to-list, push-reply-wire.
- `zt` / `zi` / `zl` / `zq`: constant tries.
- `cnt`, `pairs`, `cf`, `ccn`: leaf-mapped tree reductions.
- `tl`: trie -> first-n list, tail threaded.
- `zmq` / `zx`: multicast wiring.
- `pa`: word-trie AND-popcount.
- `sssp_core`: frontier rounds.

Missing pieces that would pay off:
- Precompiled key routers: a key's path as a DUP-free CON net, copied per round, so a keyed update costs 1 round
  per level instead of about 16. This targets the SSSP per-round path.
- Sparse tries with a merge, for frontier work that is proportional to the frontier.
- A balanced min/max combiner at hot leaves (high in-degree currently chains about 6 rounds per update).
- Lower-overhead depth computation (lg).

An author that is given this library (as words, as in Lane B) writes a graph program as a composition of these
primitives, not as scans.
