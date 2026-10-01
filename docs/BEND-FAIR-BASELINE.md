# BEND-FAIR-BASELINE: how much of the GRAPH-SWING gain is the algorithm, how much the medium? (2026-09-30)

Question: GRAPH-SWING (`docs/GRAPH-SWING.md`) hand-wrote native nets for 8 T3 programs that are 2.9-107x shallower than
the Bend of the frozen author (Luna Pro). The Bend baseline came from a weaker author, so the comparison mixes two
things: better algorithms (which any strong Bend author could port) and the medium (net tricks Bend cannot express).
To separate them, I (Opus-class, about 1.5 hours) wrote the best Bend I could for the same 8 programs, using the
same design ideas. Everything is plain Bend 0.2.38 compiled by the harness (`-O all -O no-type-check`). There are no
`hvm` blocks and nothing depends on the ADT encoding. The one non-idiomatic feature is Bend's own unscoped lambdas,
used in 2 programs.

Sources: `runs/exp7/<prog>.bend`. Verifier results: `runs/exp7/<prog>.seed{0,1}.json`. All 8 pass the hidden suite
on seed 0 and on a fresh seed 1. Per-case breakdown: `runs/exp7/compare.py` -> `compare.json`. Controls:
`walk1.bend` and `walk2.bend` (a bare list walk), `lg_adt.bend` (an ADT tree instead of a tuple tree). Metrics are
`verify_b1`'s median over the six large cases at seed 0 (n = 64/128, m up to 384), as in GRAPH-SWING.

## Result

| program | earlier Bend (Luna Pro) depth / itrs | **this Bend** depth / itrs | native (exp5) depth / itrs | earlier/native | **this/native** depth, itrs |
| --- | --- | --- | --- | --- | --- |
| t3_wsp_all_from | 1,483 / 184,806 | **891 / 63,262** | 371 / 60,872 | 4.0x | 2.40x, 1.04x |
| t3_budget_reach | 9,421 / 51,142 | **1,582 / 145,263** | 981 / 115,529 | 9.6x | 1.61x, 1.26x |
| t3_sources_sinks | 1,862 / 99,293 | **1,843 / 110,261** | 615 / 88,444 | 3.0x | 3.00x, 1.25x |
| t3_triangle_count | 2,333 / 3,454,846 | **1,401 / 194,791** | 802 / 157,680 | 2.9x | 1.75x, 1.24x |
| t3_line_graph_edges | 6,218 / 1,092,212 | **1,778 / 88,156** | 607 / 81,485 | 10.2x | 2.93x, 1.08x |
| t3_dag_longest | 49,861 / 1,579,691 | **1,544 / 64,600** | 711 / 51,330 | 70x | 2.17x, 1.26x |
| t3_cc_count | 164,351 / 890,296 | **2,121 / 301,103** | 1,536 / 256,254 | 107x | 1.38x, 1.18x |
| t3_in_out_degrees | 4,580 / 481,209 | **1,845 / 84,241** | 586 / 79,143 | 7.8x | 3.15x, 1.06x |
| geometric mean | | | | **10.9x** | **2.21x** depth |

Worst case (depth_max): cc_count 9,733 (native 10,014), wsp 4,550, dag 3,891. Everything else is 2,556-3,613.
Seed 1 medians: wsp 2,872, budget 1,862, sources 1,291, triangle 1,644, line 1,400, dag 1,533, cc 2,947, iod 764.

On a log scale, porting the algorithms closes 67% of the gap (geometric mean 10.9x -> 2.2x). Per program the
algorithmic share is: cc 93%, dag 82%, budget 79%, line 54%, triangle 48%, iod 44%, wsp 37%, sources 1%. The
earlier sources_sinks Bend was already at the Bend floor, as explained below. Interactions are now 1.04-1.26x
native on all 8 (earlier: up to 22x). The one exception GRAPH-SWING noted still holds for work: on budget_reach, the
earlier early-stopping Dijkstra does 51k interactions against 145k here.

## Where the remaining 2.2x comes from: the list walk, and nothing else

The edge list is a cons list, so every program walks it once, sequentially. I measured the Bend floor for that walk
with a bare length walk (`walk1.bend`): **9.0-9.1 rounds per edge** on all 8 programs' inputs. Per cell, the chain is
REF expansion, 2 CON annihilations to reach the tag, SWI, branch REF expansion, CON to reach the tail, then the
recursive REF. Unrolling 4 cells per call with nested `match` (`walk2.bend`) gives 9.3 rounds/edge, no better,
because each nested match becomes its own REF'd definition. The native `stream` walker reaches about 2.3
rounds/edge.

Per large case, (this Bend depth) minus (Bend walk floor on that same input) is small: 108-1,203 at the median case
(for example sources_sinks m=188: walk 1,701 of 1,843; cc m=101: walk 918 of 2,121). If the walk is replaced by the
native rate (depth - walk + 2.3m), this Bend comes to **0.57-0.97x of the native depth on every one of the 48
cases**, median about 0.9x. On the cases with few edges, where the walk hardly counts, Bend already equals native:
cc m=13 797 vs 787, m=63 (a 61-round path) 9,733 vs 10,014; triangle m=11 358 vs 371; wsp m=16 291 vs 307; budget
m=23 1,384 vs 1,369.

So the native advantage over a strong Bend author is a per-edge constant: about 9 vs 2.3 rounds per input cell,
about 3.9x on the walk. The difference in the depth medians comes from this constant times m (1.4-3.2x, largest on
the walk-only programs sources_sinks, line_graph and in_out_degrees). None of the graph-algorithmic part of the gain
is medium-specific. This is an estimate: it assumes the walk adds serially, which the per-case data support, since
the walk-adjusted ratio is stable across m.

## Design ideas: could Bend express them, and at what cost

1. **Vertex-keyed tree with updates that expand before the data exists: yes, but only with tuples.** A complete
   tree of nested pairs `(a, b)`, with an update that recurses as `switch l` / `if k & m` / `(a, b) = t` / rebuild.
   Pair destructuring compiles to a bare CON, and both switches depend only on the key and the level, so a chain of
   m updates collapses level by level (the same mechanism as native `nav`). Instances: set, inc, add, min, push-cons,
   Braun insert. The trap: the same tree as a user ADT with `match` on the node (`lg_adt.bend`) serialises the
   update chain. line_graph goes 1,778 -> 7,727, which is exactly the earlier author's 6,218 regime. Cost: none
   beyond about 6-8 rounds per level.
2. **Blocked speculative walker (K cells per pattern, eraser end-detection): no.** `match` is one switch per cell
   behind a REF, nested patterns do not fuse, and there is no end-of-list-by-erasure. The only way around it I can
   see is to apply a list value as a function (relying on the num-scott encoding). That is not Bend semantics and I
   did not use it. **This is the entire residual gap.**
3. **Wires as return addresses (multicast): yes, with unscoped lambdas.** For each edge, the walk creates
   `lambda $x: 0` as a sink in a request tree at the provider's leaf, and uses `$x` as the value at the consumer. At
   the end, each provider applies its value (auto-duplicated) to its sinks. triangle_count uses it to fetch the two
   bitset rows per edge (3.45M -> 195k interactions). dag_longest uses it to tie the DP knot: best[u] =
   max(1 + best[v]) as a dataflow net, 49,861 -> 1,544 depth, with no rounds. Cost: an escape-hatch feature. It is
   safe here only because what gets duplicated is numbers or trees of numbers (HVM2 DUPs are unlabelled).
4. **Frontier Bellman-Ford over trees (wsp, budget, cc): yes, directly.** Adjacency is stored per vertex as a Braun
   tree, so a leaf's emission is O(log deg) deep, not a list walk. Each round threads keyed min-updates into a
   fresh candidate tree, merges it leafwise with an OR-reduce, and uses the budget as an acceptance bound. A
   one-round lookahead helped in Bend: the next round's emission is spawned from D2's leaf flags before the
   OR-reduce decides whether to continue. That took cc from 2,590 to 2,121 (worst case 14,593 to 9,733) at +3%
   interactions, and budget from 1,887 to 1,582. It gives about 150 rounds per BF round, the same as native's
   about 155.

Bend-specific snags (engineering, not expressiveness): a nullary constructor with tag 0 (`Br/Leaf`) is merged with
`List/Nil` by the compiler into `@List/Nil__M_Br/Leaf`, which the harness decoder rejects. Putting `Node` first
fixes it. Tree depth, masks and bases have to be computed and threaded by hand.

## Verdict

Most of the GRAPH-SWING gain is algorithmic. On a log scale, two thirds of the headline gap (10.9x geometric mean ->
2.2x) goes away when a strong author writes Bend with the same data structures. That includes the most dramatic
cases: cc 107x -> 1.38x and dag_longest 70x -> 2.2x. The medium-specific part is real but narrow: about 2.2x
geometric mean (1.4-3.2x) on depth, and about 1.2x on interactions. It comes entirely from how fast a cons list can be
consumed: about 9 rounds/cell for Bend's compiled `match` against about 2.3 for a speculative K-cell net walker. So
the claim "the T3 loss was the author, not the medium" holds for the graph logic. The claim that native nets are
3-107x better than Bend does not survive a fair Bend baseline. The fair figure is about 1.4-3.2x, and it scales with
input length, not with graph structure.
