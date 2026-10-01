# GRAPH-SWING-2: scaling the hand-written graph nets to the T3-B family (2026-09-30)

Question: GRAPH-SWING (docs/GRAPH-SWING.md, runs/exp5) showed the T3 graph loss was the author, not the medium, on 8
programs. Does that hold across a whole family, including the programs the frozen author never got accepted?

Method: every program of `genome/corpus/t3_b.py` not already in runs/exp5 (21 of 25) was redesigned by hand as a native
HVM2 net (Opus-class author, one session, nothing searched or learned). Priority: programs with no accepted native net,
then programs where native lost to Bend on depth, then the rest. Previous-native and Bend states are combined exactly as
`genome/exp_quick.py` does. Nets are built by `runs/exp9/build.py` from per-program text (`runs/exp9/*.hvm.txt`), the
exp5 templates (`runs/exp5/lib.py`, `trie.hvm.txt`, `sssp.hvm.txt`) and the new template library
`runs/exp9/lib_ext.py`. `runs/exp9/results.py` rebuilds every net, runs `genome.verify.verify` on seeds 0, 1, 2 (with 3
workers instead of the CLI's 16, same function and suite) and writes `runs/exp9/results.json`. Metrics are the
verifier's medians over the large cases at seed 0 (as in GRAPH-SWING); the last column gives the depth medians at seeds
1 and 2.

**All 21 nets pass the hidden suite on seeds 0, 1 and 2.**

| program | before | **new depth / itrs** (seed 0) | prev native depth / itrs | Bend depth / itrs | new vs Bend (depth, itrs) | new depth seeds 1, 2 |
| --- | --- | --- | --- | --- | --- | --- |
| t3_mst_second | no native | **31,704 / 3,215,700** | none | 4,227,250 / 41,367,941 | 133.3x, 12.86x | 31,146, 31,119 |
| t3_clique_number | no native | **1,090 / 329,074** | none | 5,684,300 / 42,498,176 | 5215.0x, 129.14x | 1,312, 1,442 |
| t3_euler_start | no native | **2,799 / 764,648** | none | 2,004,563 / 6,330,606 | 716.2x, 8.28x | 2,853, 2,886 |
| t3_count_shortest_paths | no native | **2,082 / 293,579** | none | 408,094 / 1,413,385 | 196.0x, 4.81x | 3,500, 3,536 |
| t3_girth | no native | **1,613 / 834,005** | none | 420,535 / 5,144,051 | 260.7x, 6.17x | 2,112, 1,177 |
| t3_articulation_points | no native | **1,685 / 991,834** | none | 35,286 / 953,892 | 20.9x, 0.96x | 2,904, 3,289 |
| t3_lex_shortest_path | no native | **3,922 / 481,497** | none | 87,821 / 3,695,349 | 22.4x, 7.67x | 3,472, 2,953 |
| t3_greedy_coloring | no native | **962 / 87,993** | none | 7,829 / 992,550 | 8.1x, 11.28x | 564, 720 |
| t3_max_flow | no native | **480 / 1,867** | none | 940 / 2,558 | 2.0x, 1.37x | 1,935, 1,600 |
| t3_wsp_dist | native lost | **1,752 / 229,878** | 1,039,936 / 4,003,032 | 77,513 / 479,781 | 44.2x, 2.09x | 2,316, 2,190 |
| t3_kcore_size | native lost | **1,382 / 190,595** | 624,405 / 2,634,925 | 55,423 / 1,650,287 | 40.1x, 8.66x | 1,253, 1,615 |
| t3_walk_count | native lost | **856 / 991,298** | 37,855 / 6,655,009 | 4,164 / 17,673,644 | 4.9x, 17.83x | 1,042, 1,228 |
| t3_eccentricities | native lost | **2,830 / 2,927,976** | 262,434 / 209,250,754 | 32,091 / 103,248,078 | 11.3x, 35.26x | 3,086, 2,954 |
| t3_wiener_index | native lost | **2,713 / 3,246,506** | 392,153 / 346,173,975 | 61,111 / 168,185,512 | 22.5x, 51.81x | 3,047, 2,918 |
| t3_cheapest_k_walk | native lost | **1,515 / 1,050,994** | 49,036 / 18,265,030 | 9,673 / 3,467,105 | 6.4x, 3.30x | 2,390, 1,785 |
| t3_bipartite_matching | native lost | **14,171 / 1,175,062** | 261,301 / 822,631 | 133,146 / 1,282,652 | 9.4x, 1.09x | 1,703, 6,042 |
| t3_minimax_path | native won | **1,899 / 186,864** | 144,700 / 17,753,902 | 3,495,963 / 15,146,679 | 1840.9x, 81.06x | 3,583, 2,286 |
| t3_msf_weight | native won | **27,180 / 1,023,146** | 340,772 / 1,610,444 | 1,462,638 / 5,983,286 | 53.8x, 5.85x | 17,972, 32,769 |
| t3_forest_mis | native won | **2,255 / 277,085** | 82,118 / 606,486 | 166,010 / 998,373 | 73.6x, 3.60x | 2,722, 2,343 |
| t3_max_degree_vertex | native won | **521 / 61,736** | 2,981 / 177,462 | 47,979 / 263,044 | 92.1x, 4.26x | 550, 623 |
| t3_apsp_matrix | native won | **3,264 / 6,400,297** | 6,188 / 42,813,296 | 60,057 / 29,165,074 | 18.4x, 4.56x | 3,341, 3,016 |

Tally:
- **No accepted native -> native wins: 9 of 9** (mst_second, clique_number, euler_start, count_shortest_paths, girth,
  articulation_points, lex_shortest_path, greedy_coloring, max_flow). Depth beats Bend on all 9, interactions on 8 of 9;
  articulation_points does 4% more interactions than Bend at seed 0.
- **Native lost -> native wins: 7 of 7** (wsp_dist, kcore_size, walk_count, eccentricities, wiener_index,
  cheapest_k_walk, bipartite_matching), on both depth and interactions.
- Native already won (5): all improved further, on both metrics (apsp_matrix previously won depth but lost interactions,
  42.8M vs 29.2M; now 6.4M).
- Together with runs/exp5 (wsp_all_from, triangle_count, line_graph_edges, budget_reach), **all 25 T3-B programs now
  have a native net that is shallower than Bend's**; 23 of 25 also do less work (the exceptions are articulation_points,
  4% more at seed 0, and exp5's budget_reach, 2.3x).

Caveats:
- max_flow: at seed 0, four of the six large cases are trivial (s == t or s/t out of range), for Bend too, so the median
  says nothing. Worst large case: depth 12,469 vs Bend 3,223,070, interactions 1.44M vs 12.9M. Seeds 1 and 2 medians
  are non-trivial: depth 1,935 and 1,600.
- The Bend baselines are the frozen author's (some very weak: clique 5.7M depth, minimax 3.5M). As in GRAPH-SWING, most
  of the new ideas are algorithms a strong Bend author could partly port. The blocked stream walker, eraser-driven ends,
  return wires and wire-level multicast are net-only.
- Size assumptions from the corpus spec are built into several nets (see "Limits"). They hold on every suite case, but
  the nets are not general beyond the corpus's stated sizes.

## Design ideas that worked (new in this round)

1. **All-sources BFS as one bitset frontier loop (`msbfs`).** Every vertex keeps R (sources that reached it) and F (its
   frontier sources) as word tries. A round ORs neighbour frontiers into a gather trie with keyed updates, gated as in
   the exp5 core. n BFSs cost about one BFS of rounds (diameter + 1), each round costing n/16 words per vertex. Programs
   plug in a leaf hook:
   - eccentricities: the last round with new sources, 11x shallower than Bend and 35x less work;
   - wiener_index: sum of k x popcount;
   - girth: a saturating two-counter per source gives an odd closed walk (2k-1) or an even one (2k), and the loop stops
     at the first detection;
   - articulation_points: bit v is "search in G - v from v's min neighbour", and R_u starts as {u}, so u removes itself
     from its own search. The n searches run as one loop, and the cut set is OR_u(Nb_u & ~R_u).
2. **Fixed-count ungated rounds (`rounds`).** When the round count is an input (walk_count, cheapest_k_walk), no
   convergence test sits between rounds. Every vertex pushes every round, so round r+1's structure expands while round
   r's numbers still flow. Results: 856 depth vs Bend 4,164 (prev native 37,855) and 1,515 vs 9,673. This confirms the
   exp5 diagnosis: the synchronisation test, not the updates, was the per-round cost.
3. **Packed labels that let the one min-propagation core compute more.**
   - (weight, hops) as W*128+H gives lexicographic shortest paths (lex_shortest_path).
   - (root, dist) as root*1024+dist, with every vertex starting as its own root, roots a forest with no rooted input
     (forest_mis).
   - (hops, parent arc) as hops*4096+arc gives a BFS tree with parent pointers (max_flow). The emission keeps only the
     hop part and adds 4096+arc.
   - (key, parent) as key*128+parent drives Prim.
   - A semiring swap by text substitution: minimax_path is wsp_dist with max(d, w) in place of d+w, 1,899 depth vs Bend
     3.5M.
4. **A distance phase, then a gated dataflow DP.** In count_shortest_paths, forest_mis and lex_shortest_path, every
   arc fetches its tail's value through a multicast chain. A switch on d(u)+1 == d(v) either waits for the value or
   erases the wire, so only strictly closer vertices are ever awaited and there are no cycles. Path counting: 2,082 vs
   408,094.
5. **Single-pass argmin-and-take with return wires (`am2`).** Each leaf offers (packed, index, list, R) upward, where
   R is a wire back to the leaf's own slot. At each node the loser closes its R with its own value, and only the winner
   travels. The winner is marked visited and its adjacency list is handed out without a second data-keyed descent.
   Prim per step 380 -> 250 depth (mst_second 48,595 -> 31,704).
6. **LCA-free path maxima.** Ancestor rows R_v[a] = max edge from v up to ancestor a, INF off the ancestor chain, give
   maxpath(u, v) = min_a max(R_u[a], R_v[a]); the minimum is reached at the LCA. This gives second-best MST during Prim.
7. **Exchange updates for greedy decisions.** A keyed update that hands out the leaf's current value and installs a wire
   for its future value turns a sequential greedy pass (a matching) into a dataflow net that waits only for earlier
   edges at the same vertices. Seeding Edmonds-Karp with it: bipartite_matching 82,649 -> 14,171 depth and 7.5M -> 1.18M
   interactions (without it the flow net lost to Bend on work by 5.9x).
8. **Parallel forward-clique enumeration.** Each branch copies only its small candidate list, (x, N+(x) & P), not the
   matrix; the top-level lists come from the multicast pattern. Clique number in 1,090 depth vs 5.7M.
9. **Cheap exits before touching the lazy input list.** max_flow's guards (s == t, s/t out of range, no edges) answer 0
   without reading the list.

## What resisted, and why (limits of the approach)

- **Inherently sequential steps stay sequential.**
  - Prim is n steps of about 250 depth (argmin + keyed updates), so msf_weight and mst_second land at 18k-35k depth:
    still 54x and 133x under Bend, but 10-30x above the other nets. Boruvka (log n phases) would need a component
    relabel (a cc run) per phase; not attempted.
  - Augmenting paths (max_flow, bipartite_matching) are one full BFS (1,500-2,000 depth) plus an O(m) residual rebuild
    per augmentation. max_flow's worst case (seed 1) is 36,616 depth. The greedy seeding is what made matching
    competitive. The depth/work trade: plain Edmonds-Karp won depth (82.6k vs 133k) but did 5.9x Bend's work; greedy
    plus EK wins both. Push-relabel was not tried.
- **Rounds pay about 150 depth each.** Every convergence-tested loop (frontier core, msbfs, peel, vfront) pays the
  gated-emission path per round, so depth ~ rounds x 150 + a few hundred. Only fixed-count loops escape this (idea 2).
- **Work of all-sources methods.** msbfs pays n/16 words per vertex per round. articulation_points (n searches at
  once) is about Bend's work at seed 0 (0.99M vs 0.95M) and above it at seeds 1 and 2 (1.47M, 1.12M). apsp_matrix's
  dense worst case is 32M interactions (Bend's worst: 39.5M).
- **The 24-bit medium forces size-specialised encodings.**
  - Packed keys assume n <= 128 (lex_shortest_path, Prim), w <= 1000, and < 4096 arcs (flow).
  - greedy_coloring uses a 24-bit colour mask: it would be wrong if a vertex needed colour >= 24, which would take at
    least 24 lower neighbours all coloured distinctly.
  - wiener_index halves a doubled sum.

  All of these hold for the corpus sizes (n <= 128, test sizes 64/128), but a general net would need multi-word keys.
- **Hand-writing cost.** Each net took about 5-15 minutes with the template library, most of that on wiring bugs that
  the linter catches immediately: a duplicated wire, a missing `*`, subtraction operand order. Two runtime bugs were
  semantic: dead k-core leaves absorbing later decrements, and padding leaves acting as forest roots. The library is
  what made 21 programs feasible in one session.

## Template library (runs/exp9/lib_ext.py; exp5 templates reused)

| template | what it computes | programs served (of 21) |
| --- | --- | --- |
| exp5 `stream` (blocked walker) | edge-list consumption, K = 16 | 21 |
| exp5 `nav` (keyed update) | all keyed tries (actions: set, add, or, min, push, take, exchange, copy-out) | 21 |
| exp5 frontier core (`@loop`/`@sssp_start`) | min-propagation rounds; with packed labels and semiring swaps | 8 (wsp_dist, euler, count_sp, lex, minimax, max_flow, bipartite, forest_mis) |
| `mc` (multicast chains, exp5 idea 3 packaged) | fetch a vertex value at every arc (dataflow DP) | 5 (greedy, count_sp, lex, clique, forest_mis) |
| `get`/`getd`/`lk` | guarded keyed lookup | 9 |
| `minmax` | min/max by one compare + selector switch | 14 |
| `und_adj`, `und_nb` | undirected adjacency stream steps (weighted / plain) | 3 + 3 |
| `mex` / `pop` | branch-free lowest-clear-bit, SWAR popcount | 2 |
| `peel` | synchronous threshold-deletion rounds (k-core) | 1 (its keyed add/push actions reused by 9) |
| `msbfs` | all-sources bitset BFS with a per-program leaf hook | 4 (eccentricities, wiener, girth, articulation) |
| `bitrows` | bit-matrix rows, word-trie OR/AND-NOT, ascending bit listing | 2 (articulation, clique) |
| `rounds` | fixed-count ungated push rounds | 2 (walk_count, cheapest_k_walk) |
| `prim` (+ `am2`) | Prim with argmin-and-take, optional ancestor rows for second-best | 2 (msf_weight, mst_second) |
| `zrows` | unit distance rows | 2 (mst_second, apsp) |
| `vfront` | all-sources distance vectors by frontier rounds | 1 (apsp_matrix) |

Each template's docstring gives its port conventions and its depth/interaction cost.

## Files

- nets: `runs/exp9/t3_*.hvm` (21), per-program sources `runs/exp9/*.hvm.txt`, builder `runs/exp9/build.py`,
  templates `runs/exp9/lib_ext.py`
- verification: `runs/exp9/v.py <prog> 0,1,2` (one program), `runs/exp9/results.py` (all; writes `results.json`)
