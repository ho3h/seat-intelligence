# GRAPH-SWING-3: the last six T3 programs without a native net (2026-09-30)

Question: after GRAPH-SWING (runs/exp5), GRAPH-LIB (runs/exp8) and GRAPH-SWING-2 (runs/exp9), six T3 programs (all in
`genome/corpus/t3_a.py`) still had no accepted native net: t3_sp_len, t3_khop, t3_articulation, t3_tree_parents,
t3_scc_count and t3_scc_label. Can they be hand-designed from the same machinery?

Method: hand-written nets (Opus-class author, one session of about 2 hours, nothing searched or learned), built by
`runs/exp19/build.py` from the graphprims library (`genome/lib/graphprims.py`), the exp5/exp9 templates, per-program
text (`runs/exp19/*.hvm.txt`) and three new templates in `runs/exp19/lib_ext.py`. `runs/exp19/results.py` rebuilds
every net, runs the unmodified `genome.verify.verify` on seeds 0, 1 and 2 (2 workers) and writes
`runs/exp19/results.json`. Metrics are the verifier's medians over the six large cases (n = 64/128). "Bend" is the
frozen author's B1 state (`runs/g1/b1/seed0/<prog>/state.json`, `best`).

**All six nets pass the hidden suite on seeds 0, 1 and 2.**

| program | idea | **depth / itrs (seed 0)** | depth seeds 1, 2 | worst-case depth (seeds 0-2) | Bend depth / itrs | vs Bend (depth, itrs) |
| --- | --- | --- | --- | --- | --- | --- |
| t3_sp_len | BFS rounds that stop when t is reached | **1,145 / 136,615** | 925, 1,791 | 10,370 | 15,699 / 44,699 | 13.7x shallower, 3.1x MORE work |
| t3_khop | BFS with budget k; k = 0 and k = INF exit early | **585 / 38,511** | 996, 797 | 1,548 | 1,531 / 26,113 (audit fail/pass) | 2.6x shallower, 1.5x more work |
| t3_articulation | exp9 all-sources search, count instead of list | **3,855 / 3,060,226** | 3,214, 2,713 | 27,006 | 23,784,544 / 135,205,382 | 6,170x, 44x |
| t3_tree_parents | Euler tour + pointer jumping (no BFS rounds) | **2,070 / 951,216** | 2,070, 2,080 | 2,113 | 38,833 / 1,675,848 | 18.8x, 1.8x |
| (t3_tree_parents__bfs) | BFS with packed (hops, parent) labels | 3,238 / 381,499 | 2,701, 2,473 | 22,669 | | 12.0x, 4.4x |
| t3_scc_count | forward + backward bitset reachability, AND, lowest bit | **2,977 / 1,959,435** | 3,480, 2,878 | 25,725 | 462,271 / 4,764,219 | 155x, 2.4x |
| t3_scc_label | same, list of labels | **4,449 / 3,953,343** | 2,850, 2,722 | 12,799 | 882,609 / 5,804,291 | 198x, 1.5x |

Tally: depth beats Bend on 6 of 6 (2.6x to 6,170x); interactions beat Bend on 4 of 6. The two losses are the
single-source BFS programs (sp_len 3.1x, khop 1.5x more work), for the reason given under "Limits".

## How each was built

- **t3_sp_len** (graphprims `frontier` + `update` + `get`): unit-weight frontier rounds from s. New trick, an **early
  stop flag**: t's leaf starts at the marker 16777214 instead of 16777215; a leaf that accepts a candidate while holding
  the marker raises flag 2 instead of 1, and the loop goes on only while the OR of the flags is exactly 1. In
  synchronous unit-weight rounds the first value t accepts is its distance, so the loop stops after d(s,t)+1 rounds
  instead of ecc(s)+1 (seed-0 depth 1,506 -> 1,145, itrs 180k -> 137k). s == t answers 0 without reading the list;
  an unreached t turns the marker into 16777215.
- **t3_khop** (graphprims `sssp` + `reduce`): BFS with budget k (only candidates <= k are accepted, so at most k+1
  rounds), then count leaves i < n with D[i] <= k. The contract trap: the reference counts `d <= k` with d = 16777215
  for unreachable vertices, so **k = 16777215 gives n** (the exp8 Haiku probe failed exactly here). That case and
  k = 0 (answer 1) exit before the edge list is read, which alone took the seed-0 median from 136k to 38.5k itrs.
- **t3_articulation**: the exp9 t3_articulation_points net unchanged except the readout. Bit v of an all-sources bitset
  BFS is "search in G - v from v's smallest neighbour"; the cut set is OR_u(Nb_u & ~R_u), and here it is popcounted
  (`wpc`, new) instead of listed. Brute force by removal, done as n searches in one bitset loop: n <= 128 costs
  8 words per vertex per round.
- **t3_tree_parents**, two nets:
  - BFS version (`__bfs`): frontier rounds with packed labels hops*4096 + parent. The arc weight stored in u's list is
    u itself, and the message is (label & ~4095) + 4096 + sender, combined by min. The depth is rounds-bound: tree
    height x ~150, so a path costs 22,669.
  - **Euler-tour version (the deliverable; `euler`, new).** Edge i gives arcs 2i = u->v and 2i+1 = v->u. One pass
    over the out-lists sets next(a) = the out-arc after twin(a) in the cyclic list at a's head. At r, the wrap-around
    goes to a sentinel, which is the Euler tour of the doubled tree starting at r. lg(2n-1) fixed rounds of pointer
    jumping follow, packed nxt*1024 + dist, so one round is P[a] := P[nxt(a)] + dist(a), fetched through multicast
    requests. Arcs already at the sentinel are not re-requested, so no long DUP chain forms. Then u->v precedes its
    twin iff dist(u->v) > dist(v->u), and parent(v) = u. The conditional sets P[v] := u / P[u] := v are pre-wired
    while the edges are read; their keys are known at read time. Depth is flat in the tree shape (2,070-2,113 on
    every large case; the path worst case 22,669 -> 2,113) at 2.5x the BFS version's work (still 1.8x under Bend).
- **t3_scc_count / t3_scc_label** (exp9 `msbfs` twice + `wlow`/`scc_out`, new): one all-sources bitset BFS on the
  out-lists (R_v = {u : u reaches v}) and one on the in-lists (R_v = {u : v reaches u}), run in parallel. Both
  include v itself, because msbfs seeds round 0 with {v}. SCC(v) is the word-wise AND of the two rows, and the label is
  its lowest set bit: per word, p = w & -w, then popcount(p - 1), then min over words. count = #{v < n : label(v) = v}.
  This is exactly the reference's definition (mutual reachability, min id). No FW-BW recursion or colouring was
  needed.

## New templates (runs/exp19/lib_ext.py)

| template | what it computes | used by |
| --- | --- | --- |
| `wpc` | popcount of a word-trie bitset | articulation |
| `wlow` | lowest set bit of the AND of two word tries (16777215 if empty) | scc_count, scc_label |
| `scc_out` (`sccl`, `sccc`) | readout of two msbfs state tries: label list / label == self count | scc_count, scc_label |
| `euler` (`fill`, `vf`, `pjl`/`pjr`, `dv`, `cs`) | Euler-tour successor from out-arc lists, fixed-count pointer jumping over an arc trie with multicast fetches, conditional keyed set | tree_parents |

sp_len and khop needed no new template: they are graphprims compositions plus glue. sp_len adds one text patch to the
`frontier` loop test (`any == 1` instead of `any != 0`).

## Limits (what did not come out better)

- **Single-source BFS work.** A frontier round is one traversal of the whole vertex trie (G, D, C plus a fresh
  candidate trie). The fixed cost is about 15k interactions per round at n = 128, whatever the frontier size.
  - Measured on sp_len's n = 128 cases: 39k itrs with no edges at all, and about 60k of reading the list and
    building adjacency for 130 edges.
  - Bend's queue BFS pays per visited vertex, so it wins on work for sp_len (3.1x) and khop (1.5x), even with
    early stop and the k shortcuts.
  - The fix is the missing library word already named in GRAPH-SWING: sparse frontier tries, with work proportional
    to the frontier. Depth is 2.6x-14x better in any case.
- **Rounds-bound worst cases.** Every convergence-tested loop costs about 150 depth per round. msbfs-based nets
  (articulation, scc) reach 25-27k depth on long directed/undirected chains, and sp_len reaches 10k on a long path.
  tree_parents escaped this only because a tree admits the Euler-tour/pointer-jumping reformulation. A lg-round
  transitive closure (repeated squaring of the 128x128 bit matrix) would bound scc depth but costs about
  7 x 128^3/16 word operations, far more work than Bend's 4.8M; not attempted.
- **Size assumptions** (all hold for the corpus: n <= 128, a spanning tree has 2n-2 arcs):
  - packed nxt*1024 + dist needs fewer than 1024 arcs;
  - the BFS parent label hops*4096 + parent needs n <= 4096;
  - the markers 16777214/16777215 are safe because BFS distances are < n.
- **Work of all-sources methods.** articulation and scc do 0.9-4.7M interactions (n/16 words per vertex per round).
  That is still below Bend's, whose articulation is 135M.

## Files

- nets: `runs/exp19/t3_*.hvm` (6, plus the `t3_tree_parents__bfs.hvm` alternative)
- builder: `runs/exp19/build.py`; program text: `runs/exp19/scc.hvm.txt`, `runs/exp19/tree_parents_et.hvm.txt`;
  templates: `runs/exp19/lib_ext.py`
- verification: `python runs/exp19/v.py <prog> 0,1,2` (one net), `python runs/exp19/results.py [progs]` (writes
  `results.json`, log in `results.log`), `python runs/exp19/probe.py <prog> [seed] [net]` (per-case big metrics)
