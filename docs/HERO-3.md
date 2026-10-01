# HERO-3: an executor-verified auto-parallelizer (swing row 30)

Status: section 1 (kill rule, benchmark, protocol) was written and frozen on 2026-09-30 BEFORE the property tester, the
rewriter's verification or any depth measurement was run on the benchmark. Hashes of the frozen code and the per-fold labels
with their Python evidence are in `runs/hero3/PREREG.json`. Code: `genome/hero3/`. Results: `runs/hero3/`.

## 1. Kill rule, benchmark and protocol (pre-registered)

**Hypothesis.** Given a sequential fold written as a net (a walk over a list with a combining step), the executor tests
algebraic properties of the combiner on many inputs; if they hold, a mechanical rewrite turns the linear fold into a balanced
tree reduction over TREE-SHAPED input, and the executor verifies the rewritten net against the original on hidden suites.
Depth drops from linear in n to logarithmic-ish with no redesign by the author.

**What "the fold" is here (scope, stated up front).** A fold is a presentation `(unit, lift, comb, fin)` of nets plus the
original sequential step `step`. The original net is a one-cell-at-a-time list walker over `step` from `unit`; by default
`step(acc, x) = comb(acc, lift(x))`. Two folds (`avg_wrong_merge`, `adjacent_equal_wrong`) have a naturally written sequential
`step` and a *guessed* combiner. The tester does not invent combiners: it tests the combiner it is given, and it tests that the
original step IS `comb(acc, lift x)` (property H). It does not search a combiner library.

**Tree-shaped input (ingest format).** A rope `Nil | One(x) | Cat(l, r)` (encoded `(0 *)`, `(1 x)`, `(2 (l r))`), any shape.
The rewrite is correct for every shape; depth is proportional to the height the caller supplies. Two accounting modes are
reported: (i) the caller supplies the rope (the harness encodes it as data, as it does lists: cost 0 inside the net), and (ii) a
list-to-rope conversion net (`nets.L2T`, pairwise passes), whose depth is measured on list input.

**Property tester** (`genome/hero3/tester.py`). Everything is decided by running the fold's own nets inside driver nets on
HVM2; Python only builds inputs and compares. Test domain = TREE-REACHABLE states: unit, lift(x), and tree folds of ropes of
all shapes evaluated by the fold's own nets, plus states of the original walker on lists up to 30 long. Exhaustive-small:
all ropes with at most 3 leaves over the fold's small alphabet (all bracketings) give the enumerated states; all triples of
the first 14 of them. Random: 260 random ropes (0-12 leaves, shapes balanced/left/right/random with empty subtrees) and 120
random lists drawn from a wide mixture (40% 0..10, 30% 0..1000, 20% full 24-bit, 10% edge values), then 3,000 random triples,
2,000 pairs, 1,500 (state, element) pairs for H. Properties: associativity, left and right identity of `unit` on the whole
pool, H (`step(a,x) = comb(a, lift x)`), commutativity (reported, not required: the tree preserves left-to-right order, so
it is not needed for this rewrite). **Decision: ACCEPT iff associativity, both identities and H hold on every test.**
Tester seeds: 7 (decision), 8 and 9 (fresh audit; the decision must not change).

**Benchmark (44 folds, fixed).** 31 associative (label `assoc`), 12 counted non-associative (label `nonassoc`), 1 adversarial.
Associative: sum, product, length, max, min, count_even, argmax_first, argmin_first, second_largest, longest_run, is_sorted, last
(12 from the corpus t1/t2 tiers; each verified against the corpus program), xor_all, category_set (bitset union), all_positive,
any_zero, count_gt500, sum_squares, gcd, lexmin_pair, top3_merge (top-k merge), sat_sum_cap, sat_sum_24, minmax_pair, mean_floor,
hash_affine (the order-dependent hash h*31+x as an affine-map monoid), plus 6 seating-flavoured ones: category_counts (7-tuple
guests per category in a section), category_set (above), max_priority_guest, first_violation (index of the first violation),
adjacent_equal, section_fill_cap6 (saturating count at the section limit 6). Non-associative (must be rejected): sub_fold,
hash31 (h*31+x used directly as the combiner), abs_diff, alternating (b-a), sat_sub, horner_square (a*a+b), xorshift_hash,
midpoint, sat_sum_unclamped, glitch_1e3 (a merge bug firing on about 1 pair in 1000), avg_wrong_merge (sequential running
average with the tempting unweighted merge), adjacent_equal_wrong (correct sequential step, merge compares last with last).
Adversarial (`planted_point`): a sum with one planted single-point merge bug; **excluded from kill rule (a)** because no finite
sample can be required to find a one-point violation, but reported prominently (accepted or not, and whether its forced rewrite
passes the suite). Labels are by construction; per-fold Python evidence (a witness triple for every `nonassoc` fold, and no
witness for `assoc` folds on 8,000 triples of the closure pool) is in `runs/hero3/PREREG.json`.
Every fold's ORIGINAL net (sequential walker) is checked by `genome.verify` seeds 0-2 (all 44 pass, `runs/hero3/construct.json`)
and against Python models of lift/comb/step/fin (`construct.py`).

Label definition (refined before the tester was run on the benchmark; smoke runs of the tester on `sum`, `sat_sub`,
`sat_sum_unclamped`, `argmax_first` were used only to debug the driver): `nonassoc` means that `comb` is not an associative
operation with identity `unit` on the tree-reachable state domain (associativity OR an identity law fails). The first draft
of the Python evidence sampled only states reachable by the sequential walker; that was wrong (for `sat_sub` the sequential
states are all 0, so the fold is degenerate there but its tree reduction is not), so the domain is the closure of the lifts
under `comb`, in both the tester and the evidence.

**Rewrite and verification.** For each accepted fold, `nets.tree_net` builds the tree reduction (Nil -> unit, One(x) ->
lift x, Cat(l,r) -> comb of the two sub-results computed in parallel, then fin). Verification: `genome.verify.verify` on a
tree-input program whose reference is the list reference on the in-order leaves, seeds 0, 1, 2 (edge, random, exhaustive-small,
big cases up to 256 leaves, random tree shapes incl. skewed and empty subtrees); a fresh-seed audit at seeds 100, 101, 102 where
the reference is the ORIGINAL NET executed on the in-order leaves (differential against the original). For every rejected fold
the tree net is built anyway ("forced rewrite") and verified on seeds 0-2, to show what the verifier says about it.

**Kill rule.**
- (a) The tester accepts at least 80% of the 31 associative folds (at least 25) AND rejects 12 of 12 counted non-associative
  folds. Any counted non-associative fold accepted counts as a false acceptance and fails (a); if its forced rewrite also
  passes the suite it is reported as suite-indistinguishable.
- (b) At least 70% of the accepted folds rewrite to nets that pass every suite (seeds 0-2 with the Python reference and audit
  seeds 100-102 against the original net).
- (c) On balanced ropes of n = 1,000, 10,000, 100,000 leaves, measured with the depth oracle (`physics/hvm2-depth`), the fitted
  exponent of depth in n (least squares of log depth on log n, three points) of the rewritten net is at most 0.4: median over
  the verified rewrites at most 0.4 and at least 90% of them at most 0.4. The original sequential net (list input) is measured at
  the same sizes where the runtime allows (median exponent reported; expected about 1). Interactions are reported with the same fit.
- If (a) and (b) pass but (c) fails, report the exponent and the ingest cost.
- **HERO-3 is killed if (a) fails or (b) fails or (c) fails.** It is a success only if all three pass.

**Strong-human-route comparison.** For 5 folds (sum, max, argmax_first, category_counts, first_violation) a strong Bend tree
reduction on the same rope input is written by me, compiled with `BEND_OPTS`, verified with `genome.verify.verify_b1` (seeds
0-2), and measured on the same depth oracle and sizes. Bend/native ratios of depth and interactions are reported.

**Controls (reported, not in the kill rule).** (1) The same rope folded sequentially in order (`nets.seqtree_net`): the depth
win must come from associativity, not from the tree input. (2) The original walker after the swing-18 K=16 lookahead
transformation: shows the best a linear walker does. (3) The list-to-rope ingest pipeline (`nets.ingest_net`).

**Process rules followed.** No paid APIs; HVM2 executor and depth oracle only; at most 4 heavy processes; no `pkill`; `.env`
untouched.

## 2. Results

Everything below is from `runs/hero3/` (raw: `stage1_tester.json`, `stage2_verify.json`, `scale_*.jsonl`, `bend_verify.json`,
`author_audit.json`, `ingest_verify.json`, `power.json`, `crossover.json`, `shape_sensitivity.json`, `summary.json`).
Not pre-registered, added after the main numbers were in and marked as extras: the power curve (2.1), the audit against the
authored corpus nets and the authored-net depths (2.2, 2.3), the crossover (2.3), the ingest-after-lookahead variant (2.4, 2.6)
and the shape sensitivity (2.4). The kill-rule numbers do not depend on them.

Depth = rounds of the depth oracle (`physics/hvm2-depth`), interactions = its ITRS. Sizes n are leaves/elements.

### 2.0 Verdict against the kill rule

**Kill rule NOT hit. (a) PASS, (b) PASS, (c) PASS**, with the scope caveats in section 3 (the combiner is supplied, not
inferred; the win needs a balanced tree as input; from a list the win is a constant factor, not a change of exponent).

| clause | threshold | result |
|---|---|---|
| (a) accept associative | >= 25 of 31 (80%) | **31/31** accepted (tester seeds 7, 8, 9 all identical) |
| (a) reject non-associative | 12 of 12 | **12/12** rejected (0 false acceptances among the counted set) |
| (a) excluded adversarial | reported | `planted_point` (single-point bug): **ACCEPTED** by the tester at all 3 seeds and its rewrite passes all 6 suites: a false acceptance that passes the suite, as predicted in section 1 |
| (b) accepted rewrites that pass every suite | >= 70% | **32/32** (31 genuine + the planted one; 31/31 without it): 6/6 suites each (seeds 0-2 vs Python reference, seeds 100-102 vs the original net) |
| (c) depth exponent of the rewrite, n = 1k, 10k, 100k | median <= 0.4 and >= 90% of folds <= 0.4 | **median 0.109, max 0.112, min 0.074, 31/31 <= 0.4** (original list walker: median 1.000, range 0.999-1.000) |

### 2.1 Property tester (executor as the judge)

Per fold and seed 6,519-10,215 executor-checked cases (median 7,553; total 354,844 in the decision seed, 1,064,524 across the three seeds):
associativity triples (exhaustive over 14 enumerated states + 3,000 random), identity on every state of a pool of 2-386
tree-reachable states (mean 224, median 271), 2,000 commutativity pairs, 1,500 homomorphism pairs (H: original `step` equals `comb(acc, lift x)`).
One executor run per property; 3-22 s per fold for the three seeds together.

| set | folds | accepted | rejected |
|---|---|---|---|
| associative, label `assoc` | 31 | 31 | 0 |
| non-associative, counted | 12 | 0 | 12 |
| adversarial single-point bug | 1 | 1 | 0 |

Commutativity flags agree with the pre-registered labels 31/31 (23 commutative, 8 order-dependent: argmax_first, argmin_first,
longest_run, is_sorted, last, hash_affine, adjacent_equal, first_violation). The tree preserves order, so none of this was
needed for the rewrite; it would be needed if the caller's tree could permute leaves.

Reasons for the 12 rejections (first seed): associativity failed on 11 of 12 (failing triples 5 of 3,343 for `glitch_1e3` up to
5,530 of 5,744 for `xorshift_hash`); the left or right identity failed on 9; H (step != comb o lift) failed on `avg_wrong_merge` only
(as designed: natural sequential step, guessed merge). `sat_sum_unclamped` was rejected by the identity law only: the executor
sample found no associativity violation (0 of 3,343 triples) although the Python evidence has a witness (12869955, 4516890,
3938): the rejection is right, but for a different reason than the label text; a sampled test can miss an associativity
violation and be rescued by another law. `glitch_1e3` (a bug on about 1 pair in 1,000) was caught by only 5 of 3,343 triples.

**Detection power (extra, `runs/hero3/power.json`).** Sum with a merge bug that fires on nominally 2^-k of random pairs, 10 tester
seeds each; the verify suite on the forced tree, seeds 0-2:

| k | 4 | 6 | 8 | 10 | 12 | 14 | 16 | 20 | 24 |
|---|---|---|---|---|---|---|---|---|---|
| tester rejects | 10/10 | 10/10 | 10/10 | 10/10 | 9/10 | 7/10 | 1/10 | 0/10 | 1/10 |
| verify suite fails (of 3 seeds) | 3 | 3 | 3 | 3 | 3 | 1 | 0 | 0 | 2 |

The k axis is nominal: the bug masks are all-ones low bits, and the generator's edge values (16777215, 8388607) satisfy the masks
directly, which is why k = 24 is sometimes found. The tester reliably finds violations of rate 1/1,000 and above, sometimes at
1/16,000, and cannot see 1/1,000,000 or single points, and neither can the hidden suite.

### 2.2 Rewrite and verification (kill rule b)

Original nets: all 44 pass `genome.verify` seeds 0-2 (`construct.json`; 12 against the corpus t1/t2 programs, 32 against new
Programs) and agree with their Python models.

| check | folds | result |
|---|---|---|
| tree net vs Python reference, seeds 0, 1, 2 (edge, random up to 24 small + 6 big cases up to 256 leaves with random shapes incl. skewed and empty subtrees, exhaustive-small; 61 cases per seed) | 32 accepted | 96/96 seed runs pass |
| tree net vs the ORIGINAL NET (executor differential), fresh seeds 100, 101, 102 | 32 accepted | 96/96 pass |
| tree net vs the accepted corpus native nets as authored in the G1 runs (not my generated walker), seeds 100-102 | 12 corpus folds | 36/36 pass |
| forced rewrite of rejected folds, seeds 0-2 | 12 | **36/36 runs fail** (failing cases per seed: `sub_fold` 40-44 of 61, `hash31` 21-26, `abs_diff` 16-21, `alternating` 20-25, `sat_sub` 21-24, `horner_square` 20-27, `xorshift_hash` 22-26, `midpoint` 32-38, `avg_wrong_merge` 27-28, `adjacent_equal_wrong` 12-17, `sat_sum_unclamped` 2-3, `glitch_1e3` 1-2) |

So the verifier independently catches every wrong rewrite, though `sat_sum_unclamped` and `glitch_1e3` are caught by only 1-3 of 61
cases per seed, and the planted single-point bug is invisible to both the tester and the verifier.

### 2.3 Depth and interactions (kill rule c)

Balanced rope of n leaves, element values from the fold's generator (seed 5), depth oracle. Median over the 31 associative folds:

| variant | depth 1k | 10k | 100k | depth exponent (median) | interactions 100k | interactions exponent |
|---|---|---|---|---|---|---|
| **tree fold on the rope (the rewrite)** | 231 | 315 | 385 | **0.109** | 5.20M | 1.000 |
| original list walker | 10,015 | 100,015 | 1,000,015 | 1.000 | 3.90M | 1.000 |
| original + swing-18 K=16 lookahead | 10,016 | 100,016 | 1,000,016 | 1.000 | 3.81M | 0.999 |
| in-order sequential fold on the same rope (control) | 10,120 | 100,163 | 1,000,197 | 0.997 | 6.30M | 1.000 |
| list -> rope -> tree fold (ingest pipeline) | 7,852 | 75,492 | 750,585 | 0.990 | 8.70M | 0.999 |
| ingest pipeline after K=16 lookahead | 2,708 | 24,200 | 238,038 | 0.972 | 8.44M | 0.996 |

* Rewrite vs original at 100k: depth 2,341x to 4,079x shallower (median 2,812x); interactions 1.05x to 1.54x MORE (median 1.33x).
  The gain is depth only; work grows linearly and about a third larger.
* Control: folding the same rope in order (no associativity used) is as deep as the list walker (exponent 0.997). The
  logarithmic depth comes from using associativity, not from the input being a tree.
* Lookahead (swing 18) applies to all 31 walkers but shortens only 14 of them (13 by 57% at n=100k: sum, product, length, count_even,
  last, xor_all, category_set, all_positive, any_zero, count_gt500, sum_squares, mean_floor, category_counts; hash_affine by 14%). The
  other 17 are bound by the accumulator chain (comb per cell), which no list-walk trick can shorten. Tree reduction attacks exactly that chain.
* Authored originals: the accepted corpus native nets of the 12 corpus folds are also linear (11 of 12 have exponent 1.00;
  depth at 100k 0.7M-3.5M; 2,564x-6,446x deeper than the rewrite). The exception is `is_sorted`: the authored net exits at the first
  violation, so on random (unsorted) input it is shallow (3,021 at 100k, exponent 0.08, only 8x the rewrite's 388); its worst
  case (sorted input) is linear, and the rewrite has no early exit.
* Crossover (`crossover.json`): the rewrite is shallower from n = 8 leaves (sum: 54 vs 65; max 78 vs 98; longest_run 131 vs 231),
  within about 13% at n = 2-4 (longest_run is already shallower at n = 2); per doubling of n it adds 14 (sum), 22 (max), 38 (longest_run) rounds.

Per-fold table (depth at n = 1k, 10k, 100k, fitted exponent, original list walker at 100k, ratio, interaction ratio rewrite/original at 100k):

| fold | tree d 1k | 10k | 100k | exp | seq d 100k | exp | seq/tree d @100k | itrs ratio tree/seq @100k |
|---|---|---|---|---|---|---|---|---|
| sum | 151 | 203 | 249 | 0.11 | 700,075 | 1.00 | 2812x | 1.54 |
| product | 151 | 203 | 249 | 0.11 | 700,075 | 1.00 | 2812x | 1.54 |
| length | 151 | 203 | 249 | 0.11 | 700,075 | 1.00 | 2812x | 1.52 |
| max | 231 | 315 | 385 | 0.11 | 1,100,010 | 1.00 | 2857x | 1.34 |
| min | 231 | 315 | 385 | 0.11 | 1,100,010 | 1.00 | 2857x | 1.34 |
| count_even | 155 | 207 | 253 | 0.11 | 700,075 | 1.00 | 2767x | 1.46 |
| argmax_first | 245 | 337 | 406 | 0.11 | 1,000,015 | 1.00 | 2463x | 1.21 |
| argmin_first | 245 | 337 | 406 | 0.11 | 1,000,015 | 1.00 | 2463x | 1.21 |
| second_largest | 326 | 446 | 543 | 0.11 | 2,000,015 | 1.00 | 3683x | 1.14 |
| longest_run | 396 | 544 | 662 | 0.11 | 2,700,015 | 1.00 | 4079x | 1.05 |
| is_sorted | 234 | 318 | 388 | 0.11 | 1,100,013 | 1.00 | 2835x | 1.13 |
| last | 168 | 228 | 273 | 0.11 | 700,079 | 1.00 | 2564x | 1.33 |
| xor_all | 151 | 203 | 249 | 0.11 | 700,075 | 1.00 | 2812x | 1.54 |
| category_set | 153 | 205 | 251 | 0.11 | 700,075 | 1.00 | 2789x | 1.48 |
| all_positive | 153 | 205 | 251 | 0.11 | 700,075 | 1.00 | 2789x | 1.50 |
| any_zero | 153 | 205 | 251 | 0.11 | 700,075 | 1.00 | 2789x | 1.50 |
| count_gt500 | 153 | 205 | 251 | 0.11 | 700,075 | 1.00 | 2789x | 1.50 |
| sum_squares | 155 | 207 | 253 | 0.11 | 700,075 | 1.00 | 2767x | 1.46 |
| gcd | 439 | 552 | 618 | 0.07 | 1,733,436 | 1.00 | 2805x | 1.36 |
| lexmin_pair | 293 | 401 | 489 | 0.11 | 1,700,012 | 1.00 | 3477x | 1.18 |
| top3_merge | 355 | 483 | 586 | 0.11 | 2,200,024 | 1.00 | 3754x | 1.07 |
| sat_sum_cap | 261 | 353 | 429 | 0.11 | 1,300,018 | 1.00 | 3030x | 1.25 |
| sat_sum_24 | 270 | 368 | 452 | 0.11 | 1,500,010 | 1.00 | 3319x | 1.32 |
| minmax_pair | 232 | 316 | 386 | 0.11 | 1,100,011 | 1.00 | 2850x | 1.22 |
| mean_floor | 163 | 215 | 261 | 0.10 | 700,087 | 1.00 | 2682x | 1.45 |
| hash_affine | 180 | 240 | 299 | 0.11 | 700,077 | 1.00 | 2341x | 1.39 |
| adjacent_equal | 235 | 319 | 389 | 0.11 | 1,100,015 | 1.00 | 2828x | 1.13 |
| category_counts | 159 | 211 | 257 | 0.10 | 700,078 | 1.00 | 2724x | 1.18 |
| max_priority_guest | 293 | 401 | 489 | 0.11 | 1,700,012 | 1.00 | 3477x | 1.18 |
| first_violation | 251 | 343 | 412 | 0.11 | 1,000,020 | 1.00 | 2427x | 1.18 |
| section_fill_cap6 | 251 | 343 | 419 | 0.11 | 1,300,010 | 1.00 | 3103x | 1.33 |


### 2.4 Ingest cost, honestly

The rewrite consumes a rope. Two accountings:

1. **Caller supplies the rope.** The harness encodes it as data, as it encodes lists, so the ingest cost inside the net is zero and
   the depths in 2.3 apply. The rope must be BALANCED. The rewrite does not rebalance: for a left- or right-comb rope of 1,000 leaves
   the sum fold takes 14,000 / 12,004 rounds (12-14 rounds per leaf, worse than the 7 of the list walker; `shape_sensitivity.json`),
   against 151 balanced. Depth is proportional to the height of the tree the caller supplies. This is the same condition the
   swing-20 reconciliation net already imposed on its input.
2. **Start from a list.** `nets.L2T` builds a balanced rope by pairwise passes (list -> list of One -> pairs -> ... -> one rope), then the
   tree fold runs. Measured: **7.5 rounds per element** at 100k (median, exponent 0.99), i.e. no better than just walking the list,
   because the conversion is itself a list walk. After the swing-18 K=16 lookahead pass (applied by machine to the conversion net) it
   is **2.4 rounds per element** (exponent 0.97), which is 4.2x shallower than the original walker at 100k (range 2.9x-11.3x; shallower on
   31/31 folds, and shallower than the K=16-lookahead original on 31/31) at 2.2x the interactions (8.4-8.7M vs 3.9M). Both ingest
   variants are verified on the list programs (see 2.6). So from a linked list the composition of the two machine transformations gives
   a constant-factor win that is largest for chain-bound folds; it does NOT give logarithmic depth. Logarithmic depth exists only when the
   data already lives as a balanced tree (a store written that way, or the output of an earlier tree-shaped stage).

### 2.5 Strong human route: Bend tree reduction on the same rope

Five folds (sum, max, argmax_first, category_counts, first_violation), written by me as a strong Bend author would (plain recursive
`match`, independent sub-reductions, tuple state, no list), compiled with `BEND_OPTS`, `verify_b1` seeds 0-2: **15/15 pass**
(`bend_verify.json`). Same balanced rope, same depth oracle:

| fold | n | native depth | Bend depth | Bend/native depth | native itrs | Bend itrs | Bend/native itrs |
|---|---|---|---|---|---|---|---|
| sum | 1,000 | 151 | 163 | 1.08 | 36,982 | 35,984 | 0.97 |
| sum | 10,000 | 203 | 221 | 1.09 | 369,996 | 360,012 | 0.97 |
| sum | 100,000 | 249 | 268 | 1.08 | 3,700,108 | 3,600,492 | 0.97 |
| max | 1,000 | 231 | 220 | 0.95 | 50,968 | 48,971 | 0.96 |
| max | 10,000 | 315 | 299 | 0.95 | 509,982 | 489,999 | 0.96 |
| max | 100,000 | 385 | 360 | 0.94 | 5,100,094 | 4,900,479 | 0.96 |
| argmax_first | 1,000 | 245 | 292 | 1.19 | 74,950 | 67,701 | 0.90 |
| argmax_first | 10,000 | 337 | 400 | 1.19 | 749,964 | 678,979 | 0.91 |
| argmax_first | 100,000 | 406 | 481 | 1.18 | 7,500,076 | 6,795,175 | 0.91 |
| category_counts | 1,000 | 159 | 171 | 1.08 | 86,952 | 102,943 | 1.18 |
| category_counts | 10,000 | 211 | 229 | 1.09 | 869,966 | 1,029,971 | 1.18 |
| category_counts | 100,000 | 257 | 276 | 1.07 | 8,700,078 | 10,300,451 | 1.18 |
| first_violation | 1,000 | 251 | 267 | 1.06 | 83,951 | 68,231 | 0.81 |
| first_violation | 10,000 | 343 | 336 | 0.98 | 839,965 | 683,898 | 0.81 |
| first_violation | 100,000 | 412 | 413 | 1.00 | 8,400,077 | 6,845,985 | 0.81 |

Geometric mean Bend/native depth **1.06x** (range 0.94-1.19), interactions **0.96x** (range 0.81-1.18); Bend depth exponents
0.095-0.108. The machine rewrite matches a strong hand-written Bend tree reduction within about 20% on every measure and ties on
average. There is no medium advantage here; the value is that the rewrite is automatic and checked (the earlier 'author effect'
mistake is avoided by construction: both sides consume the same tree and use the same algorithm).

### 2.6 Verification of the ingest pipeline

Both list-input pipelines were verified with `genome.verify` on the list programs (corpus programs for the 12 corpus folds), seeds 0-2:
plain `ingest_net` 31/31 folds pass all 3 seeds (93/93 seed runs); after the swing-18 K=16 lookahead transformation 31/31 folds pass
all 3 seeds (93/93 seed runs) (`runs/hero3/ingest_verify.json`).

## 3. Caveats and what this does and does not show

1. **The combiner is supplied, not inferred.** The tester tests the `(unit, lift, comb, fin)` presentation it is given and tests that
   the original `step` equals `comb(acc, lift x)`. It does not search for a monoid. For the six folds where the state design is the
   real work (longest_run, is_sorted, argmax/argmin with a length field, first_violation, adjacent_equal, hash_affine) I, not the
   machine, chose the state; the corpus authors' nets are the originals for the sequential side only.
   Property H is vacuous for the 42 folds whose step is defined as `comb o lift` (it only tests the driver there) and bites on the
   2 folds with a separately written step; the corpus authors' own step nets were compared with the rewrite only by the output
   differential (36/36 on seeds 100-102), not by H. The claim that survives is:
   given a monoid presentation, the executor can check it, the rewrite is mechanical, and the verifier catches every wrong rewrite that
   it could plausibly see. 'Without the author redesigning anything' is true only for folds whose presentation is already a monoid.
2. **The benchmark is mine and the tester is a sampler.** 31/31 and 12/12 are on a set I wrote knowing the answers; the labels were
   frozen before the run (`PREREG.json`), but a fold with a rare violation is beyond both tester and suite (planted point accepted;
   power curve in 2.1). `sat_sum_unclamped` was rejected by the identity law, not the associativity check that the label named.
   The tester's guarantee is statistical.
3. **Domain matters.** My first draft sampled states reachable by the sequential walker only. That is wrong for a tree reduction (for
   `sat_sub` the sequential states are all 0), and I corrected the domain to the closure of the lifts under `comb` before running
   the tester on the benchmark (section 1). A tester that only looks at sequential states would have accepted `sat_sub`.
4. **Depth win is depth only.** Interactions grow 1.05x-1.54x (median 1.33x); both sides are O(n) work.
5. **The win needs a balanced tree** (2.4). A skewed rope is worse than the list. From a linked list the exponent stays about 1.
6. **Original baselines.** My generated walker (one cell per switch, `step` = comb o lift, branch-free arithmetic combiners) and
   12 authored corpus nets both give exponent 1; the authored is_sorted exits early. The generated walkers' per-cell chain is 7-27
   rounds, which sets the size of the 2,812x median ratio; a hand-optimised sequential walker would not change the exponent.
7. **Scope of exactness.** All rewrites were checked on the interface types (u24, tuples); a combiner that duplicates non-number
   structure could hit HVM2's unlabelled-duplicator hazard (none of the 44 did). The tree fold has no early exit, so it can lose to an
   early-exiting walker on data where the exit is early (is_sorted).
8. **Bend comparison** is my own strong Bend, not a search over Bend authors; ratios near 1 mean the rewrite is not worse than what I could
   write, not that no cleverer Bend exists. The same rewrite would be expressible in Bend; it was not built.

## 4. Files

* `genome/hero3/`: `netbuild.py` (expression DAG to net, authoring aid), `folds.py` (44 folds, labels), `nets.py` (original walker, tree
  rewrite, controls, list-to-rope), `tester.py` (property tester), `programs.py` (list and rope programs), `construct.py`,
  `prereg.py`, `run_bench.py` (stages), `scale.py`, `analyze.py`, `report.py`, `bend_trees.py`, `bend_run.py`, `author_audit.py`,
  `ingest_verify.py`, `power.py`.
* `runs/hero3/`: `PREREG.json`, `construct.json`, `stage1_tester.json`, `stage2_verify.json`, `scale_*.jsonl`, `summary.json`,
  `report.md`, `nets/*_seq.hvm`, `nets/*_tree.hvm`, plus the JSON listed at the top of section 2.
* Reproduce: `python -m genome.hero3.construct; python -m genome.hero3.prereg; python -m genome.hero3.run_bench tester; python -m genome.hero3.run_bench verify;
  python -m genome.hero3.scale tree|seq_list|seq_la|seq_tree|ingest|ingest_la|seq_author|bend; python -m genome.hero3.analyze; python -m genome.hero3.report`.
