# HERO-2: verification by normalization (swing 29, 2026-09-30)

Status: DONE. Section 1 (kill rule, corpus, protocol) was written, and the corpus frozen (sha256 recorded), before the normalizer was run on it. Sections 2-9 are results.

## 0. Verdict (short)

**Kill rule not hit. Verification by normalization works for what it can see, and it is sound on everything we threw at it, but what it can see is plumbing, not algorithms.**

* **Coverage.** 91 of the 92 known-equal pairs are proved (98.9%); 84 of 92 (91.3%) with the exact tier S alone. Synthetic 45/46, real repo pairs 46/46
  (opt.py outputs vs originals 28/28, glue vs hand-wired 2/2, recipe wrapper vs opt.py-expanded 16/16). The one miss is dead-code elimination, as predicted.
* **No false proof.** 0 of 46 known-unequal pairs proved, including 6 rare-witness mutants (differ on 6% to 57% of random inputs). Post-registration stress
  on real nets: 0 false proofs in the mutation stress (section 7).
* **Sound in sampling.** All 91 proved pairs agree with the real HVM2 executor on 240 to 400 inputs each (58,960 executor runs, 0 disagreements).
* **What it cannot see** (all measured): loop fusion, arithmetic laws (`*` is not known to commute), semantic peepholes (`x+1` written two ways),
  dead code, and restructured recursion (exp12 lookahead nets: 0/6). Wherever a proof is impossible it fails closed; it never guessed.
* **Honest strength of the word "proof".** Tier S is exact (any plugged-in graph, errors included). Tiers U, S~a and D are conditional; D is
  demonstrably wrong when the value being copied is itself a duplicator node (section 4). 6 of the 91 proofs need D, 1 needs U.
* **Hero.** "group ; filter" and "filter ; group" are proved to be the same program for every guest list (tier S), a three-stage reordering is proved (tier D),
  and two orders that should not commute are refuted with a 1-guest counterexample. Filters must be written as mask stages (branch-free) for this to work.

## 1. Pre-registration (written BEFORE the first run of the normalizer on the corpus)

### 1.1 Hypothesis
Interaction nets are confluent. Reduce a net with OPEN wires (interface ports left free, no data plugged in) using the HVM2
rules and stop at data-dependent nodes (OPR/SWI with an open operand). If two nets reach isomorphic residual graphs, then for
every way of plugging concrete data into the interface the two runs are the same run, so the nets are equal "for all inputs"
with no test suite.

### 1.2 What "proved" will mean (tiers, fixed now)
The engine (`genome/hero2/inet.py`) is an exact port of the HVM2 v2.0.22 rules (`physics/hvm2/src/hvm.rs`), including the
unlabelled DUP rule (two DUPs always annihilate) and the runtime's own REF copy rule (copy if the definition has no DUP node of its
own, abort otherwise). The normal form of a definition is computed by instantiating it and reducing; definitions are then compared
COINDUCTIVELY (partition refinement over the union of both books, REF nodes labelled by the class of their definition), so a
recursive definition is never unfolded infinitely. A pair is tried at increasing strength and the first tier that succeeds is
reported:

| tier | extra power over the previous | assumption behind an "equal" verdict |
|---|---|---|
| **S** | none: exact HVM2 rewriting + coinductive definition classes; a class also records the definition's `safe` flag | none beyond strong confluence: equal canonical forms mean the two nets are the same net after the same reductions, for ANY plugged-in graph (including malformed data), errors included |
| **S~a** | the `safe` flag is ignored when classes are compared | equal on every input on which neither net aborts with the runtime's "clone a non-affine global reference" error |
| **U** | references in aux position or on an open wire are unfolded when the definition is non-recursive and contains no DUP anywhere in its call closure ("deep DUP-free") | as S; the argument that copying such a reference equals copying its body is a sketch (section 4), tested only by sampling |
| **U~a** | U and S~a together | union of the assumptions |
| **D** | U~a plus label-oblivious DUP laws: `{a *}` is a wire, `{* *}` is an eraser, chains of DUPs are one unordered fan-out | equal on every input in which the values reaching a DUP are DUP-free data (a DUP meeting a DUP is NOT a copy in unlabelled HVM2). Not checkable from the net alone. |

Only S is a proof in the strict sense. S~a, U, U~a, D are reported as "proved under stated assumptions" and are never merged into
the S number. Nothing in this table may be added or loosened after the first run except as a bug fix, reported as such.

### 1.3 Kill rule (fixed now)
Known-equal pairs = the 46 synthetic classes F1-F6 + the 46 real pairs R1-R4 (denominator **92**). The X1 pairs are informational and in
no denominator. Known-unequal = the 46 synthetic classes U1-U5 (denominator **46**; every one has an executor witness, see 1.5).

1. **Coverage.** The normalizer must prove (at any tier) at least 50% of the 92 known-equal pairs. Reported by class and by tier. If the
   overall rate passes but the real-pair rate (R1-R4, 46 pairs) is below 50%, the verdict is PARTIAL and says so. The S-only rate is
   always printed next to the any-tier rate.
2. **No false proofs.** ZERO of the 46 known-unequal pairs may be proved at ANY tier, and no proved pair may show a disagreement in
   sampling. A single false proof kills the method until fixed; the fix is reported with the original failure, and the corpus is not edited.
3. **Soundness sampling.** For every proved pair, at least 200 random concrete inputs (real pairs: inputs from the task's own
   generator and exhaustive small sweep with fresh seeds; big digest-only cases excluded) are run through the real HVM2 executor on
   both nets; there must be no disagreement (results compared after alpha-normalising variable names; two identical failures agree).
4. **Scope report.** For the 24 graphprims primitives and the 15 recipes: what fraction is data-oblivious enough to normalize at all,
   and what breaks it. Reported with denominators.
5. **Hero demonstration (only if 1-3 pass).** Two differently composed seating-stage pipelines proved equal, one pair that should NOT
   commute shown unequal (with a witness input), and a short human-readable certificate.

Verdict scale: PASS = 1 and 2 and 3 hold (with the PARTIAL caveat above). KILLED = 2 or 3 fails and is not fixable, or 1 fails.

### 1.4 Corpus (`genome/hero2/corpus.py`, sha256 of the file at the time of writing: `e1f42d36...3ea22`)
Every case is a pair of full HVM2 books, each defining `@prog = (input output)`. The open net that is normalized is `@prog ~ (x r)`.

(a) **46 known-equal synthetic pairs** (six classes, written as text in the file):

| class | n | what |
|---|---|---|
| F1 associativity of composition | 8 | `(f;g);h` vs `f;(g;h)` built with a composition combinator on function values (numbers, pairs, lists, 3- and 4-stage, balanced vs skewed, plain redex chain vs combinator) |
| F2 identity insertion | 8 | `id` before / after / in the middle / inside a combinator / on a tuple component / on a fan-out branch |
| F3 dup/erase laws | 8 | duplicate a literal; duplicated eraser feeding dead code; `{a *}` = wire; fan-out re-association; fan-out branch exchange; duplicating a constructed pair = duplicating its parts; dead-code elimination; exchanged fan-out into a pair |
| F4 reordering independent stages | 8 | stages acting on different components of a tuple state, applied in different orders (2-, 3-stage; list and number components); statement order in the glue body |
| F5 inlining vs call | 8 | helper call vs its body: at top level, inside a recursion branch, a helper containing a DUP, helper of helper, recursion unrolled once, a leaf def replaced by its literal tree under a data-dependent switch, whole-body inlining, constant function |
| F6 wrapper vs hand-expanded | 6 | a packaged multi-stage wrapper, a wrapper taking references as holes (`twice(@inc)`, `pipe2(f, g)`), a wrapper with a dead argument |

(b) **46 known-unequal synthetic pairs**: U1 off-by-one wiring (8), U2 swapped ports (8), U3 dropped stage (8), U4 wrong constant (8),
U5 wrong operator / extra stage / non-commuting stages / map-filter order (8) plus 6 RARE-WITNESS pairs that agree on almost all
inputs (clamped decrement, `mod 1000`, sum of only the first two, saturating increment, length capped at 5, swap-when-less). These
are the adversarial cases for a false proof.

(c) **46 known-equal real pairs from the repo** (selection rules fixed before any result existed):

| class | n | rule |
|---|---|---|
| R1 | 14 | `genome/opt.py optimize(net)` (static reduction + inlining, defaults) vs the original, for every 12th (indices 0,12,...,156) of the 167 sorted native base nets in `runs/exp3/base` |
| R2 | 14 | same 14 programs, `optimize(net, inline=False)` (static reduction only) |
| R3 | 2 | glue-composed vs hand-wired: `runs/exp14/typed_*` (checked glue API) vs `runs/exp8/*` (hand-wired graphprims) for t3_degrees and t3_cc_largest |
| R4 | 16 | the 16 recipe wrappers of `genome/lib/test_recipes.py` (15 recipes): the glue-built net vs `optimize(net, rounds=3, max_size=100)` (the recipe with its calls expanded) |

(d) X1, informational, 6 pairs, in no denominator: `exp12` K=4 lookahead-transformed nets vs the original (extensionally equal, structurally
different: an honest look at what normalization cannot see).

### 1.5 Label validation (executor only, the normalizer not involved)
`python3 -m genome.hero2.gt_check`: every net lints; every known-equal pair agrees on all sampled inputs (final run: 400 synthetic / 250 real per pair);
every known-unequal pair has at least one disagreeing input. Log: `runs/hero2/groundtruth.log`, `runs/hero2/groundtruth.json`. A pair whose
label is not confirmed is reported, not silently relabelled.

### 1.6 Predictions (written before running)
S should prove F1, F2, F4, F6 and most of F5; F3 splits (S: literal, dead eraser, pair; D: `{a *}`, reassociation, branch exchange, output
swap; dead-code elimination should NOT be provable at all); `inline_leaf_under_switch` needs U. I expect the real pairs to be harder:
opt.py's static pass can remove DUP nodes, which changes the `safe` flag (so S~a), and the recipe wrappers contain DUP-heavy defs.
Guess for R1-R4: 40-70% at some tier. Primitives and recipes: almost all stop at the first switch on an open depth or list cell, so "fully
oblivious" will be near 0; the useful question is how much plumbing reduces before that.

### 1.7 Predictions against outcome
Synthetic: predicted every class provable except dead-code elimination, with F3 splitting between S and D and the leaf-under-switch case needing U: exactly what happened (S 40, D 4, U 1, one miss). Real pairs: predicted 40-70% at some tier with S~a needed for opt.py's static pass; actual 46/46, S~a never needed (opt.py's guard keeps the `safe` bits), so that guess was too pessimistic. Primitives and recipes: predicted "fully oblivious near 0": 0/39, confirmed.

### 1.8 What changed after the first run (all of it listed)
* `corpus.py` was NOT edited after the freeze (sha256 unchanged: `runs/hero2/run1.json` carries the hash it ran against).
* The first sampler ran one executor process per input and was too slow on the shared machine; it was replaced by a batched sampler (one process runs
  many inputs as a tuple of independent calls; results compared as parsed trees). Same protocol, same inputs per pair, only faster. The label validation
  was re-run with it (`groundtruth.log`: n = 400 synthetic / 250 real inputs per pair, all 144 labels confirmed, all 46 unequal pairs have witnesses).
* Not pre-registered, added afterwards and reported as such: the scope analysis regimes (section 5), the mutation stress test (section 7), the
  scramble/confluence/open-then-plug engine self-tests (section 2), the hero pipelines (section 6; the first H4 used `+100`, a multiple of 5, so the
  two orders happened to agree: a bug in my demo, fixed to `+101`; the first H2 used two masks, which is unprovable, and is now H5).
* One dev bug found by review of my own scope harness: `iterate`'s open call reused the same wire names for `init` and `final`, which silently wired
  input to output. Fixed (the harness now asserts unique wire names); the scope numbers below are from the fixed run.

## 2. What was built (`genome/hero2/`)
| file | what |
|---|---|
| `inet.py` | port-graph model of the HVM2 rules with OPEN wires (F nodes), exact number semantics for u24 and symbolic/partial operators, REF copy/abort rule, canonical form (BFS numbering anchored at the free ports, unanchored components by minimal start), the label-oblivious DUP laws (mode D), the unfold pass (mode U) |
| `prove.py` | coinductive comparison: normal form of every definition of both books, partition refinement (greatest fixpoint) with REF nodes labelled by class, tiers S, S~a, U, U~a, D, verdict |
| `corpus.py`, `gt_check.py`, `harness.py` | the frozen corpus, executor-only label validation, batched executor sampling |
| `run_corpus.py`, `soundness.py`, `summarize.py` | first run, kill-rule (iii) sampling, tables |
| `xcheck.py`, `xcheck2.py`, `confluence_check.py`, `scramble_check.py` | engine self-tests (below) |
| `scope.py` | primitives and recipes, three regimes |
| `hero.py` | seating pipelines, fusion compile, python model, certificates |
| `stress.py`, `walkcount.py`, `sa_probe.py`, `dup_boundary.py`, `abort_demo.py` | post-registration probes |

### 2.1 How the normalizer works
1. Parse both books (`genome/netast.py`), build each definition as a port graph. A definition instance is `instantiate`d fresh at every REF, exactly like the runtime.
2. Reduce with the six rules plus the extensions. A redex is only ever a principal-principal pair of two real nodes: a principal port facing an open wire (F) or an aux port never fires, so data-dependent nodes (OPR, SWI whose operand is open) stay in the graph. That IS the residual net.
3. REF: expanded only on contact with CON/OPR/SWI (`CALL`), copied by a DUP only if the definition has no DUP node of its own, otherwise the redex is left in place and flagged `abort`. A REF facing a wire is never expanded (that is what keeps recursion finite on open data).
4. The normal form of a definition is its instance reduced the same way. Definitions are compared by partition refinement: start with one class (S keeps the `safe` bit), re-label REF nodes by class, re-canonicalise, repeat until the number of classes stops growing. Two definitions in one class have isomorphic normal forms whose REF children are pairwise in the same classes, i.e. they are bisimilar.
5. The two open call nets `@prog ~ (x r)` are reduced, canonicalised with REF nodes labelled by class, and compared. Anything unclean (fuel exhausted, abort, unsupported number form, undefined REF) means "not proved".

### 2.2 Validation of the engine itself (dev checks on repo nets, none of it a proof attempt)
* **Closed nets vs the real executor:** 80 corpus programs x 3 concrete inputs = 240 runs; the engine's normal form equals the executor's printed `Result:` (compared as canonical nets) in **240/240**. Interaction counts: the executor is always at least the engine's (never fewer; min +1, median +3; exactly +1, the root call, in 77/240). The rest is the executor taking an extra step when an operator's operand is a wire that resolves later; the engine sees the number directly. Counts are not part of any proof.
* **Open then plug:** reduce `@prog ~ (x r)` with x OPEN, then plug the concrete input into the residual net and finish reducing: equals the executor's result in **180/180** (60 programs x 3 inputs). This is the direct test that partial evaluation with open wires preserves behaviour.
* **Strong confluence:** 200 nets, open call nets reduced under 4 different random schedules: canonical residuals identical in 200/200.
* **Name/order invariance:** every one of 183 nets versus a syntactic scramble of itself (renamed wires and definitions, shuffled and flipped statements, reordered definitions) is proved equal at tier S: 183/183.

## 3. Results against the kill rule (`runs/hero2/run1.json`, `soundness1.json`)

### 3.1 (i) Coverage of the 92 known-equal pairs
| class | proved / n | by first tier that proves it |
|---|---|---|
| F1 associativity | 8/8 | S 8 |
| F2 identity insertion | 8/8 | S 8 |
| F3 dup/erase laws | 7/8 | S 3, D 4; **dead-code elimination not proved** |
| F4 reordering independent stages | 8/8 | S 8 |
| F5 inlining vs call | 8/8 | S 7, U 1 (leaf def replaced by its tree under a switch) |
| F6 wrapper vs hand-expanded | 6/6 | S 6 |
| **synthetic total** | **45/46** | S 40, U 1, D 4 |
| R1 opt.py static+inline vs original (14 programs) | 14/14 | S 14 |
| R2 opt.py static only vs original (same 14) | 14/14 | S 14 |
| R3 glue API vs hand-wired (t3_degrees, t3_cc_largest) | 2/2 | D 2 |
| R4 recipe wrapper vs opt.py-expanded (16 wrappers, 15 recipes) | 16/16 | S 16 |
| **real total** | **46/46** | S 44, D 2 |
| **all** | **91/92 = 98.9%** (S only: 84/92 = 91.3%) | |

Threshold 50%: passed. Real-pair rate 100% (threshold in the PARTIAL clause 50%): passed. Time: 16.4 s for all 144 cases (largest 1.4 s).

R3 needs D because the glue API emits the fan-out of the trie depth as a differently associated DUP comb (plus the n = 0 branch as its own definition); the two nets differ only there.

X1 (informational, no denominator): the exp12 K=4 lookahead nets, which are extensionally equal to the originals, are **0/6** proved: the walker is restructured (4 cells matched per step), so the residual nets differ in size 12 vs 74 nodes. Normalization does not reason about recursion schemes.

### 3.2 (ii) False proofs
**0 of 46.** All 46 known-unequal pairs are unproved at every tier. Each has an executor witness (`groundtruth.log`; fraction of 400 random inputs that separate them: median 94%, minimum 6% for the saturating-increment mutant, 8% clamped decrement, 17% `>3` vs `>4`, 25% length capped at 5).

### 3.3 (iii) Soundness sampling
91 proved pairs x 240-400 fresh random inputs (median 250; real pairs use the task generators plus the exhaustive small sweep at fresh seeds, synthetic ones a type-directed generator with edge values 0, 1, 999, 1000, 2^24-1): 58,960 executor runs, **0 disagreements**, all batches ran (no fallbacks, no crashes).

## 4. What is and is not proved, precisely

**Tier S (84 of the 91 corpus proofs).** If the canonical forms are equal at S then, for ANY graph plugged into the interface (data, garbage, even nodes with DUPs), the two nets reduce under HVM2's rules to the same net, so they give the same result, the same runtime error, and the same non-termination. This uses only strong confluence of the fixed rule set, the fact that a definition instance is a fresh copy, and the correctness of the port of the rules (validated in 2.2). It is a statement about the executor's behaviour, so the unlabelled-DUP rule is not an assumption: DUP~DUP annihilation is one of the rules that both sides are reduced with. It is intensional and fails closed: any difference in structure, in a REF's class or in a definition's `safe` bit blocks the proof.

**What the unlabelled DUP changes.** Unlabelled DUPs matter only if you want to read a proof as "equal as mathematical functions". Two things follow.
1. *S is stronger than function equality:* it also fixes what happens on inputs that are not well-formed data (a DUP node given as input). That is why it proves less than a test suite on typical inputs would suggest.
2. *Any law that treats DUP as a copier is conditional.* Tier D (`{a *}` is a wire, fan-out re-association and exchange) is sound exactly when the values reaching a duplicator are DUP-free data. `dup_boundary.py` (`runs/hero2/dup_boundary.txt`) shows the two facts on the real executor: feeding the DUP node `{7 8}` to the two nets tier D calls equal gives `7` vs `{7 8}` for `{out *}` vs the wire, and `23` vs `22` for the two fan-out associations. On encoded inputs (numbers, tuples, lists) the laws hold; nothing in a net can check that.

**Tier S~a (0 corpus proofs, 6 stress proofs).** Equal unless a run aborts with "clone a non-affine global reference". opt.py's own warning ("inlining is not fully exact under unlabelled DUPs") is exactly this: inlining a DUP-containing definition into a DUP-free one flips the caller's `safe` bit. The prover separates these cases: in the mutation stress, 6 of the 27 `inline_call` candidates (exp3's operator, which has no guard) are proved only by S~a, and the flipped definitions are named (`sa_probe.json` for five of them, e.g. `rcons`, `edges_cons`, `find_more`, `flood`); none aborted in 320-432 fresh inputs each. Any net with an abort redex left in its reduced form is refused at every tier (`abort_demo.txt`: the executor aborts on A and returns 10 on B; all five tiers refuse).

**Tier U.** Unfolds a reference in aux position when its definition is finite (non-recursive) and DUP-free in its whole call closure. The argument that copying such a reference equals copying its body (a DUP-free closed body is copied by DUP-commutation into two fresh copies, the generated DUPs are partners and annihilate correctly) is a sketch, not machine-checked. 1 corpus proof and 10 of the 14 `inline_leaf` mutants use it; the other 4 inline a recursive definition (`check`, `take_pos`, `inc_cons`, `eval_cons`), which U does not unfold, and are left unproved.

**What no tier does:** it does not know arithmetic (`a*b*c` in two association orders differ), it does not fuse loops, it does not know that computing before a branch equals computing inside the branch, and it does not reason about termination beyond "the reductions it ran finished within fuel". It treats i24/f24/cast forms and division by zero as stuck (flagged, never proved).

**Other honest caveats.** The engine is my port of `hvm.rs`; its only external validation is the executor cross-checks in 2.2. Resource limits of the runtime (node budget per definition, memory) are not modelled. The synthetic families were written by me knowing what plumbing the normalizer sees; the real pairs are the fairer number, but they are transformations (opt.py) built from the same rewrite rules, so high coverage there is expected and is evidence that the tool reproduces the optimizer's reasoning, not that it handles arbitrary equivalences.

## 5. Scope: how much of the library is data-oblivious enough to normalize (`scope.py`, `runs/hero2/scope.json`)
Each entry definition is called with OPEN wires, one free wire per port of its declared glue signature, and reduced with the exact engine. Three regimes: **open** (every port free), **shape** (the trie-depth ports set to the literal 3, everything else free), **spine** (as shape, and list inputs get a concrete 3-cell spine with open elements). Class of the residual net: A pure plumbing (no switch, no operator, no reference left), B branch-free symbolic arithmetic (operators on open operands, nothing else), C branches on open data (a switch whose selector depends on an open port), D blocked on unexpanded definitions, E diverges (fuel).

| | terminates | open | shape (depth=3) | spine (depth=3, list length 3) |
|---|---|---|---|---|
| 24 graphprims primitives | 24/24 in all regimes | A 0, B 0, **C 24** | A 4, B 6, C 14 | A 4, B 6, C 14 |
| 15 recipes | 15/15 in all regimes | A 0, B 0, **C 15** | A 0, B 1, C 14 | A 2, B 2, C 11 |

* **Fully data-oblivious with nothing fixed: 0/39.** Every primitive and every recipe branches on an input as its first step (the trie depth, a list cell tag, a key bit, a count), and 39/39 leave a recursive definition unexpanded under that switch.
* **With the shape parameters fixed:** 10/24 primitives normalize completely to a finite branch-free net (A: `const_trie`, `mc_empty`, `mc_deliver`, `mc_deliver_keep`; B: `iota_trie`, `reduce`, `fold`, `zip2`, `zip2e`, `mapreduce`), and 4/15 recipes once the list length is fixed too (A: `list_length_and_copy`, `list_to_trie`; B: `count_where`, `count_where_trie`). Best regime per item: 14/39 = 36%.
* **What breaks the rest:** (1) a SWI whose selector is an open input, in every remaining case: key bits (`update`, `get`, `mc_request`, `adjacency`, `bcast`), the count n (`to_list`, `filter_list`), list cell tags (`stream`, and 11 of 15 recipes), frontier state and messages (`frontier`, `relax`, `sssp`, `frontier_relax`, `layered_bfs_count`), the number being bit-counted (`lg`), loop control (`iterate`). (2) Recursion never made the reducer diverge: a REF is expanded only on contact, so on open data the recursion sits behind the blocked switch. No analysis and none of the 144 corpus cases ran out of fuel. A REF loop with no data dependence at all (`@f = (x y) & @f ~ (x y)`) would, and is reported as fuel-exhausted, not proved. (3) OPR alone is not a blocker: symbolic arithmetic stays in the graph and is compared structurally (class B).
* **Reading:** the library cannot be "normalized away"; what carries the proofs is the WIRING between the words (compositions, reorderings, inlinings, wrappers), which is why sections 3 and 6 work on compositions and not on single words.

## 6. Hero: equivalence certificates for seating-stage pipelines (`hero.py`, `runs/hero2/certificates.txt`, `hero.json`)
A guest is a record `(company, category, key, alive, hint)`; company and category are the printed fields of `data/hero/luncheon.json` (categories coded ai_lab..unlabelled). The stages are the host's rules in a game, not claims about anyone: **group** = key := company mod 5; **mask_gov** = alive := alive * (category != government); **mask_bigco**, **mask_key0**, **hint**, **bump** similar. A "filter" is written as a MASK stage (multiply `alive` by a 0/1 test) and one shared `compact` step at the end drops dead guests. A pipeline is compiled into ONE list walker whose per-guest body applies the stages in order (map fusion by construction; the compiled nets equal an independent python model on 60 random lists per pipeline, fused and per-stage forms).

| pair | expected | result | tier | executor (300 random lists) |
|---|---|---|---|---|
| H1 `group ; filter` vs `filter ; group` | commute | **PROVED EQUAL** for every list and every value | S | 300/300 agree |
| H2 `group ; filter ; hint` vs `hint ; group ; filter` | commute | **PROVED EQUAL** | D | 300/300 agree |
| H3 `group ; mask_key0` vs `mask_key0 ; group` (the mask reads the key) | do not commute | not proved; **refuted**, smallest counterexample one guest `(50,1,5,1,19)`: A -> `[]`, B -> `[(50,1,0,1,19)]` | - | 73/300 agree |
| H4 `bump ; group` vs `group ; bump` (group reads the company that bump changes) | do not commute | not proved; **refuted**, one guest `(119,5,3,1,31)`: keys 0 vs 4 | - | 39/300 agree |
| H5 `filter ; filter'` vs `filter' ; filter` | commute | NOT proved (equal on 300/300) | - | boundary: needs commutativity of `*` |
| H6 H1 but one list pass per stage | commute | NOT proved (equal on 300/300) | - | boundary: needs loop fusion |

The real chart (34 seats, 19 printed organisations): both orders of H1 give the same seating (26 of 34 guests kept by the non-government mask).

The certificate the demo shows (H1, verbatim from `certificates.txt`):

```
==============================================================================
CERTIFICATE   PROVED EQUAL
  pipeline A : group ; mask_gov
  pipeline B : mask_gov ; group
      group      = group key := company mod 5
      mask_gov   = mask out government guests
      compact    = keep guests whose alive flag is nonzero (shared last step)   [compiled as: fused_net]
  verdict    : equal for EVERY guest list (any length) and EVERY field value  [tier S]
  how        : both nets normalised by the HVM2 rewrite rules with the interface (guest list in, seating out) left open;
               the residual nets are isomorphic (fingerprint 5a72c70c7bf14e87)
               per-guest body (identical on both sides): operators ['[!]', '[%]', '[*]'], 2 copy nodes, 1 switch (on the alive flag), 2 erasers
               12 definitions in 5 classes; residual 8 / 8 nodes; 4 / 4 interactions spent
  assumption : none beyond HVM2's own rewrite rules (exact)
  not shown  : that either pipeline is the right seating rule; only that A and B are the same program.
  executor   : 300/300 random guest lists agree between A and B on the real HVM2 runtime
==============================================================================
```
A refutation prints the same header with `REFUTED (counterexample found)` and the smallest input with both outputs. What the demo does NOT show: (a) that the proof covers the per-stage list passes (H6; it covers the fused compilation, whose fusion is a construction, not a theorem here); (b) commutation of filters that drop guests by branching (the branch and the stages that feed it are compared as graphs, so "compute then branch" and "branch then compute" differ); (c) two masks in either order (H5).

Design consequence, and this is the useful part for the vocabulary layer: **branch-free stage words compose into pipelines whose reorderings are decidable by normalization.** Branching filters, multi-pass compositions and arithmetic re-association are not.

## 7. Post-registration stress test on real nets (`stress.py`, `runs/hero2/stress_*.jsonl`; not part of the frozen kill rule)
The exp3 mutation operators applied to 28 native base nets (every 6th of the sorted list from index 3): the targeted peepholes (mostly exact) and random structural mutations (mostly wrong). Each candidate is compared with its original by the normalizer and by 100 executor inputs (250 for proved ones).
```
operator            n  proved&equal  FALSE PROOF  unproved&equal  unproved&differs
R:cutwire          84            10            0               0                74
R:erasub           84             0            0               0                84
R:lit              58             0            0               7                51
R:opsym            72             0            0               1                71
R:rewire           72             3            0               3                66
R:swapkids         83             0            0               3                80
T:eqz               1             0            0               1                 0
T:inline_call      27            27            0               0                 0
T:inline_leaf      14            10            0               4                 0
T:litfirst          2             2            0               0                 0
T:preset            9             0            0               9                 0
ALL               506            52            0              28               426
```
* **0 false proofs in 506 candidates** (0 of the 426 that the executor separates from the original is proved). Of the 80 candidates that agree with the original on every sample, 52 (65%) are proved (tiers S 36, U 10, S~a 6); every proved candidate agrees on all 250 inputs.
* The 28 equal-but-unproved are the incompleteness, and they are the expected kind: `preset` (`$([+] $(1 y))` vs `$([+1] y)`: same arithmetic, different net), `inline_leaf` of a recursive definition (outside tier U), `eqz` (a zero test turned into a direct switch), and random mutations that happened to be neutral (constant changes that do not matter, `swapkids`/`lit` on dead parts).
* 13 random `cutwire`/`rewire` mutants were proved and agree on 250 inputs: they are dead-wire cuts that reduce to the same net. The dead-code pair F3 in the corpus fails only because there the dead value is computed by an operator whose operand is an open input, which never reduces.
* `walkcount.py` (`runs/hero2/walkcount.json`): the exp3 candidate that was accepted on seed 0 and rolled back on seeds 1-2 (`t3_walk_count`, `inline_call`): all 21 single-site inlinings and the joint one are proved at tier S and agree on 250 inputs; I could not reproduce a functional failure (the rollback may have been about the other metrics, or about the digest-wrapped big cases that this sampler excludes).

## 8. Caveats and what this does and does not change
1. **Easy corpus, honest reading.** The synthetic classes were written by me with the normalizer's semantics in mind and the real pairs are optimizer outputs built from the same rewrite rules. 98.9% is the coverage of "equalities that are themselves HVM rewrites plus wiring", not of program equivalence. The stress test (65% of neutral mutants) and the boundary cases (X1 0/6, H5, H6, F3 dead code, `preset`) are the fairer measure of the ceiling.
2. **Conditional tiers.** 7 of the 91 corpus proofs are not tier S (D 6, U 1). S is a theorem-like statement about the executor; D and U carry stated assumptions, and D was shown false for a duplicator-node input.
3. **Sample-based validation of the engine.** 240 closed runs, 180 open-then-plug runs and the 58,960 soundness runs are evidence, not a verification of my port of `hvm.rs`.
4. **Bounded claims.** Equality of normal forms says nothing about termination on the inputs where both loop, about resource limits, or about the `run-c` scheduler beyond "same rules".
5. **The hero result depends on a design rule** (branch-free stages, fusion by construction). That is a property of how the vocabulary is written, not of the tool.
6. **Next steps that would extend the reach**, in order of cost: an arithmetic tier (commutativity/associativity of `+ * & | ^` on numbers) would prove H5; case-splitting on a switch selector (bounded symbolic execution) would let branching filters be compared; a proof of a fusion law by checking one unfolding of the two recursion schemes coinductively would cover H6 and the X1 lookahead pairs. None is implemented.

## 9. Reproduce
```
python3 -m genome.hero2.gt_check 400 250            # label validation (executor only)
python3 -m genome.hero2.run_corpus runs/hero2/run1_synth.json F U ; python3 -m genome.hero2.run_corpus runs/hero2/run1_real.json R X
python3 -m genome.hero2.soundness runs/hero2/run1.json runs/hero2/soundness1.json 400 250
python3 -m genome.hero2.summarize                    # tables of section 3 and 5
python3 -m genome.hero2.xcheck 80 3 ; python3 -m genome.hero2.xcheck2 60 3 ; python3 -m genome.hero2.confluence_check ; python3 -m genome.hero2.scramble_check
python3 -m genome.hero2.scope runs/hero2/scope.json
python3 -m genome.hero2.hero                         # certificates
python3 -m genome.hero2.stress SHARD NSHARDS OUT.jsonl 6 ; python3 -m genome.hero2.stress_summary
```
(`run1_synth.json`/`run1_real.json` were merged into `run1.json`.)
