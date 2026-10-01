# Word filling: LLM-free authoring from input/output examples (swing 22, exp13, 2026-09-30)

**Verdict: PASS. The kill rule is not hit.** On 150 held-out generated tasks, word filling solves 81% of covered tasks with 3
examples and no feedback, and 99% when it gets the same counterexample feedback the LLM authors get. Coverage is 100% of the
four target families with the extended library and 66% with the core library. Numbers: `runs/exp13/SUMMARY.txt`. Code:
`genome/exp13/`.

## What was built

* **Words** (`genome/exp13/words.py`). There are 24 parametric list words. I wrote each one by hand as a single HVM2 net
  template, with the hole's constants emitted as literals.
  * Stages: `map E` and `filter P`. `E` is one of x*a+b, xor, and, +c, x*x, mod, div, or a predicate turned into 0/1. `P` is
    one of >k, <k, >=k, even, odd, x mod m = r. Also `take k`, `drop k`, reverse, collapse-runs, running sum, insertion sort,
    running max, running min, running xor, and diff.
  * Reducers: sum, count, max, min, xor, first, last, count-greater-than-first, argmax, and idxfirst P, idxlast P, idxsum P.
  * Every template defines `@prog = (l out)`, so words compose with `genome.compose.compose_nets`.
  * Unit tests: 65 word instances, each at hi 10 and hi 1000, each through `genome.verify` on seeds 0 and 1. All 65 pass
    (`runs/exp13/word_tests.log`).
* **Search** (`search.py`). A bottom-up enumerator with observational-equivalence merging over stage sequences.
  * A state is the tuple of example lists after some stages. It searches breadth-first by number of stages, with simple
    words and round constants tried first.
  * Hole grids are wider than taskgen's own constants: 180 predicates, 309 map expressions and 517 stages in total.
  * List outputs go up to 3 stages, pruned by length. The last stage is filled deductively: maps through a value index,
    take and drop k solved from the lengths, filters through per-value predicate bitmasks.
  * Number outputs go up to 2 stages plus a reducer. Index reducers are allowed only after at most 1 stage.
* **Lowering** composes the template nets with `c{i}_` name prefixes. The composed net is verified on seeds 0, 1 and 2.
* **Evaluation** (`evaluate.py`, `truth.py`, `summarize.py`).
  * Tasks: 150 held-out tasks (pipeline 50, reduce 50, scan 25, position 25). Indices are 20000 and up, and none is in any
    taskset.
  * Examples: 3 per task, drawn with the task's own generator at sizes 4..12.
  * Coverage: each task's ground-truth shape is parsed from its description. The search never sees it.

## Results (held-out, n=150)

| | |
|---|---|
| Coverage, core library (words named in the brief) | 99/150 (66%); 52 of 65 distinct shapes |
| Coverage, extended library (+ scan and position words) | 150/150 (100%) inside the search space |
| Solved, k=3, no feedback (net passes seeds 0, 1, 2) | **121/150 (81%)**: pipeline 72%, reduce 84%, scan 100%, position 72%; core subset 76% |
| by ground-truth size: 1 / 2 / 3 words | 93% / 65% / 38% |
| Spurious fits (fit the examples, fail the hidden suite) | 29/150 (19%). Every other found program also passed as a net: 0 lowering failures |
| Python-level solve rate for k = 3 / 4 / 5 / 6 / 8 / 10 examples | 81 / 83 / 83 / 85 / 87 / 89% |
| With counterexample feedback (at most 8 rounds) | **148/150 (99%)**. 121 solved in 1 round, 17 in 2, 10 in 3-7 |
| Search time per task | median 26 us, mean 8 ms, max 0.39 s. No timeouts. Median 2 OE classes, max 18,853 |
| Verify time (3 seeds, about 95 HVM runs each) | median 3.9 s. The executor is the only real cost |

**Why the spurious fits happen.** More examples barely help (still 16 wrong at k=10), because the task generator rarely
produces inputs that tell the candidates apart:

* collapse-runs is invisible when values drawn from 0..999 never repeat next to each other;
* `and 63` looks like the identity when every value is below 63;
* `filter x>10` looks like `x>4` when the values are 0..9;
* dedup-then-drop and drop-then-dedup differ only on repeated values.

The hidden suite's edge cases and small exhaustive sweep catch these. A single counterexample usually settles it, which is
why feedback lifts the rate from 81% to 99%.

The 2 tasks still unsolved with feedback are constant-empty pipelines (for example odd-filter then even-filter). The grid
has no `take 0`: this is a gap in the grid, not in the method.

**Outside the four families.** On 30 `sortlike` tasks (search only, k=8), 18 are solved: topk 8/8, dedup 9/11, kth 1/3.
Median (a length-dependent index) and second-largest (4 stages) have no word (`runs/exp13/sortlike_probe.txt`). Tasks
whose input is a number, a tree, a pair or a triple (rangefn, arith, treefold, zip2, tree*, recon*) are outside the
list-word library entirely.

## Against LLM authors

* **Solve rate.**
  * Luna Pro solves 95% of training-distribution tasks (785/824), with up to several attempts and verifier feedback.
  * Fine-tuned Qwen3-4B gets 14% pass@1 on the fair iid test and 31% on its own training tasks
    (docs/METHODOLOGY-REVIEW.md).
  * Word filling gets 81% with no feedback and 99% with it, on held-out tasks of the same families, and uses about 1 ms of
    CPU in total.
  * Its failures are different in kind. It never writes a broken net (0 lowering failures), but it can confidently pick the
    wrong program when the examples are ambiguous.
* **Net quality.** Setup: 60 of 80 training tasks that have an accepted, audited Luna Pro native net
  (runs/datagen/native/seed0) were solved at k=6. The other 20 were spurious fits with no feedback. Metrics are the seed-0
  verify metrics at the largest inputs.
  * Interactions, composed ÷ LLM: geomean 1.11x (median 1.02x).
  * Depth, composed ÷ LLM: geomean 0.87x (median 1.00x). Ours is shallower on 28 of 60 tasks.
  * The worst cases show the cost of composing without fusion. For `map(and 7); first`, the LLM computes `first mod 8`
    from the head alone (depth 522), while the composed net maps the whole list (1,803). For `reverse; map; map`, the LLM
    fuses the two maps.
  * Scan and position words are shallower than the LLM's (depth 0.50x and 0.79x).

## What it would take to be a real Genome author

1. **An LLM proposes and search fills.** The LLM reads the description and emits a shape plus hole types ("filter by a
   threshold, then running sum"). It could emit several of them. The enumerator fills the constants from the examples, and
   the executor verifies. This removes the LLM's failure mode (wiring) and the enumerator's (ambiguous examples: the
   description settles `x>10` versus `x>4`). The description alone also covers the 19% spurious-fit gap with no extra
   queries.
2. **A library that grows from verified LLM nets.** Every verified LLM net is a candidate word. Lift its literals into
   holes, which is mechanical for the OPR constants, re-verify it at several constants, and add it to the grid. Median,
   second-largest, zip and tree words would come in this way. Use the existing inducer (genome/induce.py) to find reusable
   subnets.
3. **Fusion at lowering.** Rewrite rules such as map;map → map, map;first → first;apply, and filter;count → count-if, or
   the exp3 inline/call-fusion pass. These close the interaction gap to the LLM, and past it where a hand-fused net exists.
   Depth needs parallel words (the K-cell walkers of the graph work), not sequential walkers.
4. **Wider types.** Words over pairs, trees and triples, and a typed enumerator. The OE trick carries over unchanged, and
   search cost is not the limit (at most 0.4 s here).
