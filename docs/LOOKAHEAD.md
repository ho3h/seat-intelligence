# LOOKAHEAD: the K-cell list walker as a machine-applied transformation (swing 18, 2026-09-30)

Question: BEND-FAIR-BASELINE found that the only medium-specific advantage left after a strong Bend baseline is the
blocked speculative list walker. It reads K cells ahead in one pattern and gets end-of-list for free by erasure: about
2.3 rounds per cell, against about 9 for a one-switch-per-cell walk. A person wrote that walker by hand in runs/exp5.
Can a program apply it to ordinary author nets, keep the semantics exact, and keep the gain?

Answer: yes. Kill rule not hit. The transformer is `genome/exp12/lookahead.py` and the harness is
`genome/exp12/evaluate.py` + `analyze.py`. Results are in `runs/exp12/` (`results.jsonl`, `summary.json`, the
transformed nets in `nets/`, and `shortlists*.json`).

## What the transformer does (an AST pass over genome/netast trees, parameterised by K)

1. **Find list patterns.** A list pattern is `((?((@N @C) CTX) PL))` anywhere a list is consumed: def roots, redex
   sides, nested CON trees, and patterns split over redexes, which a local static reduction joins back together.
   PL is either a payload wire inside CTX or a `(h t)` pattern whose wires are in CTX. The key of a walker is `(N, C)`,
   and CTX gives the shape of its arguments.
2. **Turn patterns into calls.** Each key gets a synthetic walker `@<C>_lw`. Every inline pattern, whether it is the
   author's inline tail recursion (map_inc, map_double) or the root of a wrapper def, becomes a call to it.
3. **Find the continuation of C.** The tail wire has to reach exactly one call `@W' ~ (t X)`. On the way the pass may
   do static reduction, inline a non-recursive wrapper (for example `@sum` becomes `@sum_lw`), lift a switch back out
   of a substituted tree, and hoist the call out of both branches of a switch when both continue on the tail. The
   hoisting handles nested switches, as in max/min keep/take and in paren_depth's close/open→keep/raise. The
   continuation of `(N, C)` is whichever key W' belongs to.
4. **Chains.** Cell 1 uses key k and cell i+1 uses cont(key_i), for up to K cells. That makes the author's manual
   unrolls into multi-state blocks: length has 8 hand-unrolled states, and append, count_even and product have 2.
   Handoffs become blocks too: prefix_sums moves from its first-cell walker to its scan walker. Cells 1..K-1 run
   `C_la`, which is C with the tail call replaced by a wire into the next cell's context (for sources_sinks this is
   exactly lib.py's hand-written `_cons`). Cell K runs C itself, which calls the next block.
5. **Nil branches must erase the payload slot.** A Nil payload `*` then erases every speculative cell, SWI and
   context past the end, so no length test is needed. The per-cell work is unchanged, runs in list order, and threads
   the accumulator, state and output wires.

## Evaluation

Nets: accepted, audit-clean native nets found the way opt_eval does (30 T1, 30 T2, 40 T4), plus the 8 runs/exp5 T3
nets as shipped (already K=16) and rebuilt with the one-cell stream (`build.py <p> 1`, in `runs/exp12/exp5_k1`).
Each net was run with K in {2,4,8,16}, and every result was verified with `genome.verify` on seeds 0, 1 and 2
(3 processes at most). Depth and interactions are the medians over the large cases at seed 0. "Best K" is the
passing K with the lowest depth.

| set | nets | applies | pass (all K, 3 seeds) | median depth gain, best K | median itrs change | median size growth |
| --- | --- | --- | --- | --- | --- | --- |
| **T1+T2+T3 (kill-rule set)** | 76 | **51 (67%)** | **51/51** | **-43.5%** | -0.1% | 2.3x |
| T1+T2 | 60 | 40 (67%) | 40/40 | -45.1% (35/40 at least 10%) | -0.2% | 3.3x |
| T3 exp5 rebuilt at K=1 | 8 | 8 | 8/8 | -52.1% | -0.1% | 1.5x |
| T3 exp5 as shipped (K=16) | 8 | 3 (inner walkers only) | 3/3 | -0.8% | +0.1% | 1.04x |
| T4 | 40 | 7 (18%) | 7/7 | -64.6% | 0.0% | 2.6x |

By K (kill-rule set, median depth gain / median change in large-case itrs / median change in small-case itrs):
K2 -29% / +0.3% / +2.7%; K4 -42% / -0.3% / +5.2%; K8 -44% / -0.2% / +11.6%; K16 -44% / 0.0% / +31%.
No transformed net failed on any seed at any K (232 transformed nets x 3 seeds).

**Walk-bound walkers** (sum, last, reverse, filter, map, partition, dedup, histogram) reach the stream floor, which
is 1801 → 631 depth at n=256, or 65%. **Chain-bound walkers** stop improving once the per-cell work chain dominates:
max/min/argmax -50/-44% (saturated at K2-K4, about 8 rounds per cell), prefix_sums -43% (saturated at K4). Where the
list walk is not the hot loop, the gain is small: insertion-sort family -11 to -15%, bignum -15%, lis 0%, mode 0%.
Two nets get worse: is_sorted is +7% deeper (it already had a hand-written two-cell pattern) and paren_match gains
nothing. A deployed pass should keep the original net when it is not better.

**T3: the transformer reproduces the hand-written walker.** Transformed K=1 rebuilds against the hand-written K=16
nets, by depth: sources_sinks 616 vs 615, line_graph 608 vs 607, dag 711 vs 711, in_out 587 vs 586, triangle 802 vs
802, wsp 367 vs 371, budget 973 vs 981, cc 1495 vs 1536. cc and budget come out a little ahead because the
transformer also blocks the SSSP emission walker (`em`). For cc that costs +21% interactions.

## Effect on native vs Bend

**Frozen-author Bend (state `best` of the accepted B1 nets, 91 programs solved by both arms, T1/T2/T4).** Transformed
nets use their best K; untransformed nets keep their original numbers.
- Native wins (opt_eval metric, max of the itrs and depth gains > 0): 76 → **80 / 91**. Median gain 22% → **34%**.
- Depth wins: 69 → **75 / 91**. Median Bend/native depth 1.28x → **1.47x**. By tier: T1 1.27 → 2.21x, T2 1.29 → 1.63x,
  T4 1.29 → 1.34x (only 6 T4 programs transformed).

**Strong Bend (docs/BEND-FAIR-BASELINE.md, runs/exp7, 8 T3 programs).** Geometric mean of Bend depth / native depth:
- plain one-cell native (K=1 rebuild): 1.09x, so the graph algorithms alone are at parity;
- after the machine transformation: **2.22x**, the same as the hand-written walker (2.21x).
The whole residual medium advantage is therefore obtained automatically, with no hand work.

## Does the lookahead width cost interactions? (`runs/exp12/shortlists*.json`, n = 0..512)

Yes, but the cost is a bounded constant, not a factor. Each unused speculative cell costs about 12-13 interactions
to erase. On an empty list, K16 costs +155-200 interactions and +30 rounds over the original. At n=256 every K is
within ±1% on interactions (map-like producers pay about +17% throughout for the rebuilt output conses). The best K by
depth follows the length: n ≤ 1: K1-2; n = 2-4: K4; n = 5-7: K8; n ≥ 8: K16, with K8 and K16 tied up to n ≈ 64. Chain-bound
walkers saturate earlier (max: K2, prefix_sums: K4). Recommendation: **K=4 for inputs up to about 16 (authoring
sizes: +5% interactions), K=16 for inputs of 64 or more, K=8 as the single default**: within 3% of K16 depth at
n=256, and +12% small-case interactions against +31% for K16. The block length is fixed at compile time. A
runtime choice would need the length, which walking to find would cost as much as the walk itself.

## Limits (what it does not transform)

- **Zip/merge walkers**, where two lists advance in lockstep and the tail is passed as data to the other list's walker:
  dot, intersect, merge, merge3, union.
- **Early exits**, where one branch drops the tail: nth, upper_bound, search, second_largest, paren_prefix. Blocking
  them would stay correct (speculation gets erased) but costs an erase walk, so it is not done.
- **Continuations that depend on a branch** into different walkers (tokenize, brackets3's scan), and walkers that
  consume the tail in the root pattern (parse, to_rpn helpers).
- **Non-list recursion**: tree walkers with two recursive calls (most of T4), and loops without a list pattern (range,
  replicate, take, collatz, gcd, ...). zip_add and drop/take switch on something other than the list tag first.
- **Assumption**: the Nil payload is `*`, which is the list encoding. A two-variant ADT whose variant 0 carries a
  payload would make the next cell's switch fire speculatively. The Nil-erases-slot check guards the semantics, and
  verification guards the rest.
- **Size**: net text grows 2.3x at the median (up to 9.7x for length's 8-state unroll at K16).

## What to automate next

1. A **zip lookahead** that blocks two lists in lockstep, covering 5 T1/T2 programs.
2. **Reassociating the accumulator chain inside a block** (reduce the K heads as a tree, then fold once) for
   max/min/argmax/prefix. This is where the remaining depth is: about 8 rounds per cell against 2.3.
3. **Early-exit blocking**, with the erase cost priced by the verifier.
4. Running the pass **inside the optimizer (genome/opt) and the author loop**, as a standard verified rewrite with
   K picked per net from the verifier's metrics (keep the original when it is not better).
