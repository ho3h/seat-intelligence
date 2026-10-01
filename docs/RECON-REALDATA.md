# RECON-REALDATA: the reconciliation core on real OpenSanctions data, 2k to 100k entities (swing 20, G4 slice, 2026-09-30)

**Question.** RECON-SWING showed that connected components with canonical id = largest member are shallow on HVM2 once the
input has been read. It also found three limits: the linked-list input made depth Theta(m), `hvm gen-c` + clang did not
finish on big inputs, and the Rust interpreter overflowed at n = 32,768. This swing asks whether the core runs on real
analyst judgements at 100k entities, exactly, with shallow depth and the tooling scaling.

**Verdict: yes, and the kill rule is not hit.** At every size (N = 2k, 8k, 32k, 100k) the net reproduces the Python
union-find output exactly (canon list plus must-not-link conflict list, compared by digest). This holds on both the Rust
interpreter and the native arm64 C runtime. The best net's depth goes from 1,449 to 2,172 while N grows 50x (exponent
0.10). On the same data, the RECON-SWING list-input net needs 7,436 / 23,241 / 102,095 at 2k / 8k / 32k. The 100k run
takes 4.7 s on the native runtime and 47 s on the interpreter, with 5-6 GB peak RSS. A single end-to-end net that
also runs the order-dependent must-not-link greedy matches the RECONCILIATION-SPEC step-4 reference exactly at all four
sizes (depth 6,238 -> 8,224, exponent 0.07; 13.0 s on the C runtime at 100k). Raw speed is not competitive, and it was never expected to be: a hand-written C union-find does the 100k slice
in 1.3 ms, about 3,650x faster than the HVM2 C runtime. The HVM2 C runtime is also about 22x slower than a Python
union-find.

## Data slices (`genome/exp16/data.py`)

- Source: `data/opensanctions/pairs-20251209.json.gz`, compacted once to integer pairs (`pairs-compact.pkl`, gitignored).
  Positive closure gives 459,763 clusters. There are 27 gold conflicts (negatives inside a positive cluster). They lie in
  20 clusters of sizes 1-61, and **11 of the 27 are self-pairs** (an entity judged "not the same" as itself).
- Slice of N entities: only **whole positive-closure clusters**. The 20 conflict clusters come first, then clusters in
  order of first appearance in the file, until N entities are reached. Slice ids 0..N-1 are a **seeded random
  permutation**, so ids and input order carry no cluster information. The encoder only ever sees the edge list.
- Accepted edges: every positive judgement inside the slice, score 1000. Noise edges: every negative inside the slice,
  score uniform in [0, tau), tau = 600, so they exercise the threshold and are all rejected by the net. Must-not-link
  pairs: the same negatives.

| N | accepted edges | noise edges / must-not-link | clusters | LP rounds R | max degree |
| --- | --- | --- | --- | --- | --- |
| 2,000 | 1,917 | 213 | 191 | 6 | 33 |
| 8,000 | 7,754 | 1,010 | 680 | 6 | 33 |
| 32,000 | 30,702 | 11,068 | 3,017 | 8 | 33 |
| 100,000 | 71,139 | 13,464 | 31,220 | 17 | 33 |

## Input encoding and tooling (what removed the three limits)

- **Shallow input.** Input is `(n, L, tau, E, HE, M, HM)`. E is a perfect binary tree of edges `(u (v s))` of height
  HE, padded with rejected dummies. M is a perfect tree of must-not-link pairs `(a (b live))`. Both are built directly as
  data. Subtrees of 512 leaves (about 1.5k nodes) spill into their own definitions, far below 4,095 nodes. The text
  nesting, and so the parser's recursion, is about 10 levels deep.
- **Shallow output.** The digest net folds the output to two numbers inside the executor, so readback stays trivial.
  With tree input plus digest, the unmodified Rust interpreter runs 100k at the **default 8 MB stack** (checked). The
  runner still raises the soft limit to the hard limit, but that is not needed.
- **Native arm64 without compiling the input.** `genome/exp16/hvmc_main.c` `#include`s HVM2's own runtime source
  unmodified (`physics/hvm2/src/hvm.c`, INTERPRETED mode) and is compiled once with clang -O3 -mcpu=native (8 threads,
  TPC_L2=3, because the machine is shared and has a load of about 16). It loads the book from a file holding exactly the
  buffer `hvm run-c` would pass to `hvm_c()`. That buffer is taken from `hvm gen-c`'s `BOOK_BUF`; the compiled C is
  discarded. Every input is data, so there is no multi-MB C file and no clang at run time. Serialising takes 1-18 s of
  harness time, which is not counted. The C runtime's hard limits are 16,384 definitions and 2^29 nodes; the 100k book
  uses about 400 definitions.

## The net (`genome/exp16/net.py`, variant `fan`; hand-written, nothing searched)

1. **Channels without a sequential read.** Each accepted edge leaf makes two fresh wires c1, c2 and a *sparse* vertex
   trie with two paths, to u and to v. The path leaves hold the channel ends `(c2 c1)` and `(c1 c2)`. A rejected leaf
   gives the empty trie `(0 *)`. The tries are merged pairwise up the edge tree (`@mg`): an empty side is taken as is,
   two present nodes recurse, and at a vertex leaf the two channel collections are joined. Each merge level waits only
   for the tags of its inputs, so the merges pipeline. The build costs about c * (HE + L) depth instead of about
   2.3 * m.
2. **Fan processes instead of channel-list walks.** At the vertex-leaf merge, the two channel-likes `(i o)` are joined by
   a persistent `@fan` process. The fan is itself a channel-like: the value from above is copied into both children by a
   DUP chain, about 1 rewrite per level. The children's answers are max-reduced on the way up, and only the recursion is
   gated by a switch, one round at a time. So a vertex always sees exactly one channel per LP round. The `list` variant
   keeps RECON-SWING's per-round walk of a d-long channel list, costing about 6d per round. That list is what made the
   degree-33 hubs in this data expensive (depth 2,754 vs 1,449 at 2k). The `bal` variant collects channel ends in
   difference lists and pairs them once into a balanced fan tree. Its rounds are cheaper, but it pays a one-time pairing
   cost, so `fan` is shallower here.
3. **Densify, LP, output.** `@dz` turns the sparse trie into the dense `(i ch)` trie. RECON-SWING's pipelined
   label-propagation core `cc_pipe` runs unchanged on it (persistent vertex processes, lagged global decision, k = 2).
   Then `tl_leafmap` builds the canon list with all cells in parallel.
4. **Must-not-link detection in the net.** Each must-not-link leaf puts two probe wires on a and b through the same
   sparse-trie merge. After LP, `@pz` sends every vertex's final label into its probes. The leaf compares the two labels
   and emits `(a b c)` into a difference-list output when they are equal.

Difference lists (`(hole result)`) are the key encoding trick. Concatenation is two wire connections and needs no
traversal, so the channel, probe and conflict collections never add sequential depth.

## Results (`python3 -m genome.exp16.report`; raw JSON lines in `runs/exp16/*.log`)

Depth and interactions come from the depth oracle on the bare net. Correctness is checked on the Rust interpreter and on
the arm64 C runtime (8 threads), both with the digest. Seconds are the runtime's own TIME. The interaction counts of the
fan variant depend on the scheduler: 425M on the depth oracle and 561M on the interpreter and C at 100k. The extra count
is speculative fan rounds that some evaluation orders run before the stop decision arrives.

**fan (primary)**

| N | depth | interactions (oracle) | correct Rust / C | Rust interp s | arm64 C s | max RSS Rust / C MB |
| --- | --- | --- | --- | --- | --- | --- |
| 2,000 | 1,449 | 6,837,589 | yes / yes | 0.58 | 0.19 | 146 / 96 |
| 8,000 | 1,485 | 30,602,364 | yes / yes | 2.61 | 0.47 | 638 / 408 |
| 32,000 | 2,030 | 165,670,768 | yes / yes | 13.82 | 2.22 | 3,415 / 1,992 |
| 100,000 | 2,172 | 424,833,116 | yes / yes | 46.91 | 4.67 | 6,163 / 5,134 |

Scaling exponents from 2k to 100k: **depth 0.10**, interactions 1.06, Rust interpreter time 1.12, C runtime time 0.82.
The C runtime's time exponent is below 1 because fixed costs dominate at small N. Depth per entity falls from 0.72 to
0.022. Across the four sizes the depth grows with R (6 -> 17) and with log n. It does not grow with m.

**Other variants** (all exact at every N):

| N | list: depth / C s | bal: depth / Rust s / C s | full (with greedy): depth / Rust s / C s |
| --- | --- | --- | --- |
| 2,000 | 2,754 / 0.16 | 1,539 / 0.76 / 0.13 | 6,238 / 1.31 / 0.32 |
| 8,000 | - / 0.40 | 1,636 / 3.09 / 0.39 | 6,446 / 5.68 / 0.63 |
| 32,000 | - / 1.68 | 1,895 / 8.13 / 1.18 | 7,014 / 22.12 / 3.13 |
| 100,000 | - / 5.56 | 2,674 / 31.54 / 3.95 | 8,224 / 70.11 / 13.00 |

The `full` net does about twice the work of `fan` (839M interactions at 100k). Its depth is `fan`'s plus the second,
label-keyed trie build plus the greedy of the largest conflicted component (about 3.5k, fixed across N); exponent 0.07.
Two depth-oracle runs at 100k (`full` and the list baseline, launched at the same time) exited with no output and no RSS
figure; both were rerun by hand and completed normally (records marked `note` in the logs).

**Same data, RECON-SWING net with linked-list input** (`runs/exp10/t5_reconcile_canon.hvm`, `genome/exp16/baseline_list.py`,
exact at every size it ran): depth 7,436 (2k), 23,241 (8k), 102,095 (32k), 206,490 (100k). That is 5x, 16x, 50x and 95x deeper
than `fan`, and the gap grows linearly with m, as RECON-SWING predicted. It does less work (4.2M interactions at 2k vs
6.8M), because it builds no sparse tries. Note that with the digest this net also runs at 32k and 100k (Rust interpreter, 35 s at 100k): the overflow reported in
RECON-SWING came from printing and reading back the 32k-element result, not from the net.

**Wall-clock context** (`genome/exp16/baselines.py`, union + canon only, parsing excluded, all exact):

| N | Python union-find | Rust union-find (x86_64, Rosetta) | C union-find (arm64) | HVM2 fan, arm64 C runtime | ratio to C union-find |
| --- | --- | --- | --- | --- | --- |
| 2,000 | 0.0023 s | 17 us | 11 us | 0.19 s | ~17,800x |
| 8,000 | 0.0091 s | 54 us | 53 us | 0.47 s | ~8,800x |
| 32,000 | 0.042 s | 613 us | 560 us | 2.22 s | ~4,000x |
| 100,000 | 0.21 s | 1.3 ms | 1.3 ms | 4.67 s | ~3,650x |

Union-find wins on raw speed by three to four orders of magnitude, as expected, and is 22x faster even in Python. The
reasons are in the work, not in the depth. The net does about 4-6k interactions per entity: sparse-trie merges,
(R + k) LP rounds over every vertex and channel, probes and output. Union-find does about 10 memory operations per edge.
The runtime also ran at about 120 M interactions/s on 8 threads of a loaded machine, versus the ~800 MIPS peak recorded
in gates/STATUS.md. USE-CASE requirement 6 (within 10x of a hand-written union-find) is **not met** by this net, and no
tuning of the same algorithm will close a gap of 3,650x.

## Must-not-link (RECONCILIATION-SPEC step 4, no size cap)

Route: unconstrained LP, then the ordered greedy only inside the conflicted components. This is exact for the following
reason. Merges only happen inside an LP component. A merge in a component that contains no violated pair can never be
blocked, and components are independent. At every N, the composed result equals the full greedy over the whole slice
(canon array and skipped-merge list), checked three ways:

1. host-side greedy on the net's conflict list (`genome/exp16/mnl.py`);
2. one HVM2 greedy net per conflicted component (`genome/exp16/greedy.py`, the partition route; 20 nets, all exact);
3. **one end-to-end net** (`genome/exp16/net_full.py`, variant `full`). Every accepted edge also probes u. After LP,
   vertices, edges and conflicting pairs are routed into a second sparse trie keyed by the component label. Labels
   without a pair reply their label to their members. Conflicted labels build a cell tree from their member list and run
   the greedy, and the cells carry the members' reply wires. The greedy is switch-free on its critical path: per edge,
   cu and cv are a tree sum, blocked is a check over the component's pairs rewritten into labels, and the relabel is a
   tree map. The encoder lays the edge tree out in processing order (descending score, ties ascending (u, v)). The
   output is canon after the greedy, the conflicts, and the skipped merges.

Counts at every N:

- The net detects **27/27 gold conflicts** in **20/20 conflicting clusters**, exactly as the Python reference does.
- The greedy skips 14-15 merges; the count depends on slice ids through tie order.
- **16/16 of the non-self gold pairs** end up in different clusters. The 11 self-pairs cannot be separated by any merge
  policy, so only **9 of the 20 conflicting clusters** end up fully consistent.

The greedy is sequential by specification. Its depth is set by the largest conflicted component (61 members, 61 edges,
4 pairs): 3,539 on its own net, about 58 per edge. It is the same at every N, because the conflict clusters are the same.

## Honest limits

- **Speed**: see the table above. Reproducing the work is not the bottleneck on a laptop; the HVM2 constant is.
- **Memory**: peak RSS is 5-6 GB at 100k on either runtime. The full net at 32k needs 5 GB on the interpreter. The heap
  cap (2^29 nodes) is not reached, but the 1M-entity file would need either about 10x the live nodes or partitioning.
  Partitioning by whole clusters is valid here, because components never cross clusters.
- **Depth still grows with R** (the LP diameter) and with a vertex's fan depth (log of its degree). R = 17 at 100k comes
  from long chains in the id permutation. Hooking plus shortcutting would bound it by O(log n) rounds, at more work per
  round.
- **Slice composition**: every slice starts with the 20 conflict clusters, so small slices over-represent them. Beyond
  that, slices follow file order, not a random sample.
- **Processing order** for the greedy comes from the input layout (encoder sort), not from an in-net sort. In this data
  all accepted scores are equal, so the order is ascending (u, v).
- **Bend version**: not attempted (optional, time).

## Files

- `genome/exp16/`: `data.py` (slices), `net.py` (list/fan/bal variants), `net_full.py` (end-to-end with greedy),
  `greedy.py` (greedy nets), `mnl.py`, `run.py` (encoder, executors, exact checks), `hvmc_main.c` (native driver),
  `uf.rs` / `uf.c` / `baselines.py`, `baseline_list.py`, `report.py`, `show.py`.
- `runs/exp16/`: `*.log` / `*.jsonl` results, `recon_tree.hvm` (list variant), built binaries.
- Reproduce: `NET=fan python3 -m genome.exp16.run {rust|native|depth} 2000 8000 32000 100000`, `NET=full ...`,
  `python3 -m genome.exp16.mnl ...`, `python3 -m genome.exp16.greedy ...`, `python3 -m genome.exp16.report`.
