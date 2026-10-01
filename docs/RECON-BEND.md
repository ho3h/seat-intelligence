# RECON-BEND: the reconciliation pipeline in the best Bend I could write (swing 27, G4 fairness, 2026-09-30)

**Question.** The PRD requires the human-language baselines (B1/B2) to get the same author quality as the native arm.
RECON-REALDATA (swing 20) ran hand-written native HVM2 nets for the reconciliation core on real OpenSanctions slices
(2k to 100k entities) but did not try Bend. Here I (Opus-class, the same author profile as the native nets, about
1.5 hours of writing) wrote the best Bend I could for the same pipeline. It receives the same input text and runs on the
same runtimes. The question: does Bend keep up as N grows, or fall off?

**Verdict: Bend keeps up. The G4 advantage over the human route is not shown.** The kill rule applies. At the largest N
(100k), the Bend program for canonical ids plus conflict detection is **1.02x** the native `fan` net in depth and
**1.34x** in interactions. The end-to-end program (with the ordered must-not-link greedy) is **0.90x** the native `full`
net in depth and **0.99x** in interactions. Both are well within 1.5x on both metrics. The scaling exponents are the same
as native: depth 0.13 vs 0.10 and interactions 1.07 vs 1.06 for the core; depth 0.06 vs 0.07 and interactions 1.03 vs
1.07 end to end. Every completed run is exact against the Python reference (digest): the Rust interpreter at every N,
the depth oracle with the digest (both programs at 100k, `full` at 2k), and every Bend run on the arm64 C runtime that
finished. The multi-threaded C runtime is not fully reliable for either arm at 32k-100k (see Honest limits). Bend is not faster than union-find either: all the RECON-REALDATA wall-clock
caveats carry over unchanged.

## Input encoding: byte-identical to the native arm

`genome.exp16.run.encode_input` produces `(n (L (tau (E (HE (M HM))))))`. E and M are perfect binary trees of CON pairs,
with leaves `(u (v s))` and `(a (b live))`, and subtrees of 512 leaves spill into their own definitions. Bend encodes a
tuple as plain CON pairs, so this text **is** the Bend value `(n, L, tau, E, HE, M, HM)`. Here E is a nested-pair tree
whose leaves are 3-tuples `(u, v, s)`, and M likewise with leaves `(a, b, live)`. The Bend program is `def prog(x)` with
`(n, L, tau, E, HE, M, HM) = x`. It walks E and M by switching on the known heights HE and HM, and destructures
`(l, r) = E` / `(u, v, s) = E`. So Bend gets exactly the same data, the same tree shape and the same spill definitions,
byte for byte (`genome/exp21/run.py:assemble`). For `full`, the edge tree is laid out in processing order, as for native.
The output is Bend-encoded lists. The harness digest for Bend values (`genome.bend_io.gen_digest_bend`) folds them to two
numbers, which are compared with `py_digest` of the Python union-find reference, as in exp16. The compile command is
`bend gen-hvm -O all -O no-type-check` (`genome.bend_io.compile_bend`). Bend's `@main` is dropped and the harness's main
applies `@prog` to the input. Native runs load the book as data in exp16's `hvmc_main.c` driver
(`runs/exp16/hvmc_arm64_t3`, 8 threads).

## The Bend program (`genome/exp21/recon_cps.bend.tmpl`, `full.bend.tmpl`)

Plain Bend 0.2.38: user ADTs with `match`, `switch` on numbers, tuples, first-class functions, and Bend's own unscoped
lambdas (`lambda $x: ...` / `$x`, the same feature BEND-FAIR-BASELINE used). There are no `hvm` blocks and nothing that
depends on the ADT encoding. The algorithm is the native one, expressed in Bend:

1. **Scatter once, with wires.** Each accepted edge leaf creates two channels. `lambda $a: 0` is a sink into which u will
   feed its label stream, and `$a` is that stream as seen by v; symmetrically for `$b`. The leaf builds two sparse
   single-path tries (to u and to v) holding `(input, sink)`, and the tries are merged pairwise up the edge tree with
   `match`-based merges. These pipeline (the next level's merge needs only the tags of its inputs), so the build costs
   about 25 depth per level of HE + L. Must-not-link leaves place probe sinks the same way.
2. **Weight-balanced channel ropes.** At a vertex leaf, the two channel collections are joined by a weight-balanced join
   (`cj`). Each rope node carries its children's sizes, so the new top node is known after one match and the descent
   pipelines. A hub of degree 33 gets a max-tree of depth 6 instead of the 7-10 that the plain merge order gives.
3. **Vertex processes.** A vertex's label stream is `[i, l1, l2, ...]`, with `l(r+1) = max(l(r), heads of inputs)`. The
   max is `if b > a` (Bend inlines it into a switch without REFs). The stream is fed once to all sinks, and Bend's
   automatic duplication makes the multicast.
4. **Continuation-passing flag and decision streams.** Each round emits a change flag. The flags are OR-ed elementwise up
   the trie into G, and the decision stream is `D = [1]*K ++ G`, tied back into the trie with one more unscoped lambda.
   Streams are written as `cell(v, next) = lambda k, e: k(v, next, e)` and consumed by applying the cell to a top-level
   function (`a(orl_k, b)`). The recursion therefore runs only when the cell exists, costing two annihilations and one
   expansion per level, where a list `match` costs a tag switch plus several REF expansions.
5. **Output.** Final labels go into the probe sinks, and each must-not-link leaf compares its two probes. `canon` is
   emitted from the trie of final labels with the tail threaded. `full` adds a second, label-keyed sparse trie (members
   with reply sinks, edges in processing order, conflicting pairs) and runs the greedy per conflicted label with
   switch-free arithmetic per edge: tree sums for cu and cv, an OR over the pairs, and a tree map for the relabel.

What a straightforward port looks like, and what each idea bought (depth / interactions on the oracle, K = 4):

| N | first version: plain ropes, list flags | + weight-balanced ropes | + CPS flag streams (final) | setup + output only |
| --- | --- | --- | --- | --- |
| 2,000 | 1,653 / 8.8M | 1,459 / 8.9M | **1,359 / 8.5M** | 779 / 4.6M |
| 8,000 | 1,656 / 38.3M | - | **1,446 / 37.2M** | 878 / 21.5M |
| 32,000 | 2,085 / 193.5M | 2,016 / 196.7M | **1,638 / 187.8M** | 984 / 113.5M |
| 100,000 | 3,244 / 612.7M | 3,261 / 618.0M | **2,225 / 568.7M** | 1,059 / 257.9M |

Even the first version, which took about 15 minutes to write and was correct on its first run, is 1.14x / 1.28x native
at 2k. At 100k it reaches 1.49x depth and 1.44x interactions, right at the kill line. Its per-round cost was about 85-100 depth. Two things
bound it: the max-tree over the deepest (unbalanced) hub rope, and the latency of the global stop decision. That latency
comes from the list-based OR reduce, with two ADT matches per trie level per round, which forced K = 4-6 speculative
rounds. Balanced ropes cut the data path, but at K = 4 the decision latency still bound (3,261 at 100k; K = 6 gave
2,563). The CPS streams cut the decision latency, and K = 4 became optimal (K sweep at 100k: K=3 2,418, K=4 2,225,
K=5 2,279, K=6 2,333).

## Results (`python3 -m genome.exp21.report 4`; raw records in `runs/exp21/results.jsonl`, `native_rerun.jsonl`)

Native depth and oracle interactions are the exp16 figures (same slices, same input). The C runtime columns are a
same-session rerun of both arms, interleaved per N on the same (shared, loaded) machine. Seconds are the runtime's own
TIME. Each figure pools every run of that arm, program and N: the first matrix, a 3x timing rerun, and
`genome/exp21/crepeat.py` (one serialised book run up to 8 times under a hard kill). The table gives the minimum and
median over the runs that finished correctly. The machine was shared with other agents (load 5-9), so single runs vary by
up to 5x. The Rust interpreter columns come from single runs (native: exp16 logs).

#### Core: Bend `recon_cps` (K=4) vs native `fan` (same slices, same input text)

| N | depth Bend / native | ratio | interactions Bend / native (oracle) | ratio | C runtime s, min / median: Bend; native | C runs (wrong, hung): Bend; native | peak RSS MB Bend / native (C) | Rust interp s Bend / native | exact Bend: Rust / oracle+digest |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2,000 | 1,359 / 1,449 | 0.94x | 8,488,143 / 6,837,589 | 1.24x | 0.06 / 0.06; 0.07 / 0.07 | 1 (0, 0); 1 (0, 0) | 104 / 96 | 0.49 / 0.58 | True / - |
| 8,000 | 1,446 / 1,485 | 0.97x | 37,208,419 / 30,602,364 | 1.22x | 0.14 / 0.14; 0.21 / 0.21 | 1 (0, 0); 1 (0, 0) | 438 / 408 | 2.19 / 2.61 | True / - |
| 32,000 | 1,638 / 2,030 | 0.81x | 187,814,470 / 165,670,768 | 1.13x | 0.40 / 0.98; 0.54 / 0.93 | 12 (0, 0); 4 (0, 0) | 2,178 / 2,172 | 11.31 / 13.82 | True / - |
| 100,000 | 2,225 / 2,172 | 1.02x | 568,740,022 / 424,833,116 | 1.34x | 1.03 / 3.14; 2.25 / 3.75 | 12 (0, 1); 12 (0, 0) | 5,319 / 5,588 | 34.51 / 46.91 | True / True |

Exponents 2,000 -> 100,000: depth Bend 0.13, native 0.10; interactions Bend 1.07, native 1.06
C runtime min seconds: Bend 0.73, native 0.89

#### End to end: Bend `full` (K=4) vs native `full` (same slices, same input text)

Bend depth / interactions are for the program with its output folded to one number inside Bend (genome/exp21/sumout.py; see the text); the bare-output figure is in brackets.

| N | depth Bend / native | ratio | interactions Bend / native (oracle) | ratio | C runtime s, min / median: Bend; native | C runs (wrong, hung): Bend; native | peak RSS MB Bend / native (C) | Rust interp s Bend / native | exact Bend: Rust / oracle+digest |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2,000 | 5,902 [5,817] / 6,238 | 0.95x | 14,732,125 / 12,515,494 | 1.18x | 0.08 / 0.08; 0.23 / 0.23 | 1 (0, 0); 1 (0, 0) | 179 / 174 | 0.87 / 1.31 | True / True |
| 8,000 | 6,121 [6,081] / 6,446 | 0.95x | 58,653,285 / 49,919,799 | 1.17x | 0.23 / 0.23; 0.84 / 0.84 | 1 (0, 0); 1 (0, 0) | 681 / 663 | 3.50 / 5.68 | True / - |
| 32,000 | 6,345 [6,270] / 7,014 | 0.90x | 277,085,721 / 246,705,955 | 1.12x | 0.78 / 1.12; 0.75 / 1.53 | 4 (0, 0); 12 (1, 0) | 3,174 / 2,604 | 16.07 / 22.12 | True / - |
| 100,000 | 7,434 [1,805] / 8,224 | 0.90x | 829,936,526 / 839,117,130 | 0.99x | 1.52 / 3.46; 3.34 / 6.16 | 9 (0, 1); 9 (1, 0) | 5,795 / 4,694 | 48.28 / 70.11 | True / True |

Exponents 2,000 -> 100,000: depth Bend 0.06, native 0.07; interactions Bend 1.03, native 1.07
C runtime min seconds: Bend 0.75, native 0.68

**A note on `full`'s depth at 100k.** The bare-output depth-oracle run of the Bend `full` program at 100k stops after
499M interactions at depth 1,805, and it does so repeatably. The Rust interpreter, the C runtime and the oracle with the
digest attached all do 837M and are exact. Any consumer on any one of the three outputs (a sum over the skipped list, over
the conflict list, or over the final-label trie; three variants) makes the oracle do the whole job, 830-832M at depth
7,385-7,428. So the bare figure is an oracle artifact, and I report the depth of the program with its output folded to a
number inside Bend (`genome/exp21/sumout.py`, value checked against Python, at all four N). At 2k-32k the folded figures
are 40-85 deeper than the bare ones, which are listed in brackets. I did not find the cause within the time box. The
recon program does not show it: bare 568.7M plus the 5.4M digest equals the Rust count exactly.

## What limited Bend, and what did not

- **Depth: nothing structural.** With unscoped lambdas as wires, Bend expresses the native design: per-edge channels,
  persistent vertex processes, multicast by duplication, probes and replies. The one idea BEND-FAIR-BASELINE found
  inexpressible (the K-cell list-lookahead walker) is not needed here, because the input is a tree. The remaining costs are
  per-level constants. A `match` costs about 2-3x a native CON annihilation plus SWI, which shows in the setup (about 25
  depth per trie level). Bend also needs K = 4 speculative rounds where native uses k = 2. These roughly cancel against
  the balanced ropes, which native `fan` does not have. So depth is 0.81-1.02x native at every N.
- **Interactions: +13-34% for the core, +12-18% end to end (-1% at 100k).** Bend's per-node costs are higher: path
  construction, match-based merges, constructor calls as REFs, and K = 4 instead of 2 speculative rounds (about 15M
  interactions per round at 100k). The core's ratio grows from 1.13x at 32k to 1.34x at 100k, mostly because R + K grows
  from 13 to 22 rounds and each Bend round costs a bit more than a native one. Against native `fan` on the Rust and C
  runtimes, where its scheduler-dependent speculative rounds run (561M), the Bend core does 574M, 1.02x. Bend's count is
  the same on all three runtimes.
- **What would make Bend fall off:** a design without wires. Without unscoped lambdas, a vertex can only read its
  neighbours' labels through a shared tree. HVM2 duplicates data eagerly, so a label tree fanned out to m readers is
  copied, not shared (O(n) per reader). The fallback is re-routing all messages through sparse-trie merges every round,
  about c * 2L depth per round, which I estimate (not measured) at about 3x native depth at 100k. The fairness doc
  already counts unscoped lambdas as legitimate Bend.
- **Wall-clock and memory:** on the arm64 C runtime the two arms are at parity within the noise. Minimum over correct
  runs at 100k: 1.03 s (Bend core) vs 2.25 s (native `fan`), and 1.52 s vs 3.34 s end to end. Medians are 3.14 vs 3.75 s
  and 3.46 vs 6.16 s. Peak RSS is 5.3-5.8 GB for both (Bend core 5.3 GB vs native 5.6 GB; Bend `full` 5.8 GB vs 4.7 GB).
  On the Rust interpreter, Bend is 1.2-1.6x faster at every N (34.5 s vs 46.9 s for the core at 100k). None of this
  changes the RECON-REALDATA conclusion: a C union-find does 100k in 1.3 ms.

## Honest limits

- One author wrote both arms' designs (the native nets in swing 20, this Bend in swing 27). The Bend reuses the native
  design ideas. That is the point of the fairness check, but it is not an independent human baseline.
- K was tuned per program on these slices (K = 4 for both). The native nets used k = 2 without a sweep.
- The greedy is sequential by specification. Bend and native both pay about 60 depth per edge of the largest conflicted
  component (61 edges), which sets about 3.7k of `full`'s depth at every N.
- The unscoped-lambda features are an escape hatch in the sense of BEND-FAIR-BASELINE. Two Bend snags came up. An
  unscoped variable must not appear in a `case _:` branch, because Bend expands the catch-all per constructor and then
  reports a duplicate binder; the body moves into a helper. An unused `z = f(x)` is kept, which is what the sinks need.
- The oracle artifact above.
- **C-runtime flakiness, both arms.** 2 of 33 Bend C runs at 32k-100k never finished: `recon_cps` at 100k hung
  once in 12 runs (killed after 3 h) and `full` at 100k once in 9 (killed at 90 s). 2 of 21 native `full` C runs
  returned a wrong result: at 32k an undecodable digest, and at 100k a wrong digest with 843,795,947 interactions against
  the usual 843,820,561. The single-threaded Rust interpreter and depth oracle are deterministic, and every run on them is
  exact. So these are races in HVM2's 8-thread C runtime rather than program errors. They are recorded in
  `runs/exp21/crepeat.jsonl` and `native_rerun.jsonl`.
- **Re-verification.** Another agent ran `pkill -f hvm` at about 05:00 local. The oracle runs from that window, 04:55-05:07,
  include the 32k plain-version point (2,085 / 193.5M) and the 32k setup-only point (984 / 113.5M) used in the iterations
  table. Both were rerun at 09:05 and reproduced exactly. One run from that window died (plain `recon`, setup only, 2k:
  no output); its rerun gave 779. Every number in the main tables comes from runs made after 05:10, and the oracle is
  deterministic: repeated runs gave identical depth and interaction counts.

## Files

- `genome/exp21/recon_cps.bend.tmpl` (final core), `recon.bend.tmpl` (first version), `recon_bal.bend.tmpl`
  (balanced ropes only), `full.bend.tmpl` (end to end), `diag_nogreedy.bend.tmpl` (diagnostic: greedy replaced by a
  plain reply; 2,022 vs 5,779 depth at 2k, so the greedy is about 3.7k), `run.py` (compile, assemble, run and check;
  modes rust / depth / depthd / native), `sumout.py`, `native_rerun.py`, `report.py`.
- `runs/exp21/`: `results.jsonl`, `native_rerun.jsonl`, `*_k*.bend` / `*_k*.hvm` (the compiled books), logs.
- Reproduce: `VAR=recon_cps K=4 python3 -m genome.exp21.run {rust|depth|depthd|native} 2000 8000 32000 100000`, the
  same with `VAR=full`, `python3 -m genome.exp21.sumout 2000 8000 32000 100000`,
  `NET=fan python3 -m genome.exp21.native_rerun native N...`, then `python3 -m genome.exp21.report 4`.
