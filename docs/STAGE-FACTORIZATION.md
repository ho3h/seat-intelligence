# STAGE-FACTORIZATION: a small model emits stage words, verified templates and fixed glue build the net (2026-09-30)

Swing 21 variant. Swing 17 showed that language models fail on program STRUCTURE (native_v1 pass@1 62% -> 16% -> 1% for
1-, 2-, 3-stage pipelines), not on wiring. Here the model writes no net at all. It emits a STAGE SEQUENCE over a fixed
vocabulary of verified parametric words. Each word is one hand-written HVM2 net template from the word-filling swing
(`genome/exp13/words.py`, 65/65 instances pass `genome.verify` at seeds 0 and 1). The fixed glue of `genome/compose.py`
wires the templates into one net, and `genome.verify` checks that net at seed 0. Nothing the model writes is trusted.

Code: `genome/exp15/` (lang, data, sample, score, metrics, report, train.sh, eval.sh). Results: `runs/exp15/`
(`summary.md`, `summary.json`, `pass_vs_size.svg`, `samples/*.scored.json`, `gold_*.json`, `vcache.json`). Adapters:
`adapters/exp15_*`. Paid API spend: $0; local MLX only. Nothing frozen was touched.

**Verdict: KILL RULE NOT HIT, with a large asterisk.**
- On covered iid tasks, the 1.7B stage model passes 480/480 samples (100%, 120/120 tasks covered), against 14.4% for
  the plain 4B net LoRA. The paired gain is +85.6 points [80.9, 90.1].
- Depths 3, 4 and 5 (and 7 and 8, beyond training) are flat at 100%. A 0.6B model is enough.
- The asterisk: on this templated text the model is doing what a regex parser does with 100% accuracy, and the
  hand-designed vocabulary mirrors the generator's stage list. The depth problem is removed by construction, not
  learned.
- The real open problem is reading language. On unseen wording, single-template models get 43-78%, and an untuned 4B
  given the vocabulary gets 53%. Three training wordings raise it to 93%.

## Setup

- **Stage language** (`lang.py`). One word per line: `map lin 3 7`, `map xor 255`, `map ind gt 20`, `filter gt 5`,
  `filter modeq 3 1`, `take 3`, `drop 2`, `reverse`, `dedup`, `runsum`, `sort`, `runmax`, `runmin`, `runxor`, `diff`, and
  one optional final `reduce sum|count|max|min|xor|first|last|cntgtfirst|argmax|idxfirst P|idxlast P|idxsum P`. A strict
  parser turns the text into word terms. `exp13.words.net_program` builds the templates and composes them with
  `compose_nets`.
- **Coverage.** The gold word program of every test task, assembled and verified: iid 120/120, deep 180/180
  (`runs/exp15/gold_*.json`). So the vocabulary covers the whole iid_test (60 pipeline + 60 reduce). Across the 14
  taskgen families it expresses pipeline, reduce, scan and position (40/40 each of the first 40 indices). It expresses
  none of sortlike, arith, rangefn, treefold or the six holdout families, whose types are trees, tuples and triples
  (`runs/exp15/family_coverage.json`).
- **Data** (`data.py`). There are 6,000 train and 150 valid (task text -> stage program) pairs. They are built from
  taskgen's own stage objects (`_stage`, `REDUCERS`) with a separate seed. Half are pipelines of 1-6 stages. The other
  half are reduce tasks: 0-4 stages plus a reducer. The gold program is parsed from the templated description by
  `exp13.truth`, and its Python semantics are checked against the task reference. **Split by task:** no training
  program equals a test program (174 candidates were dropped). Word *shapes* do overlap: 88/120 iid shapes occur in
  training. For the deep sets the overlap is 31/40 at depth 3, 11/40 at depth 4, 2/40 at depth 5, and 0 at depths 7-8.
- **Prompt** (`lang.prompt_stage`). It follows the prompt_short style: task text plus input and output types. It has no
  primer, no vocabulary list and no task id.
- **Test sets** (`runs/exp15/sets/`), all unseen tasks:
  - `iid`: the 120 tasks of `data/tasksets/iid_test.json`.
  - `deep`: fresh pipelines with 3, 4 and 5 stages (40 each), plus 7 and 8 stages (30 each; longer than any training
    pipeline, which tops out at 6).
  - `novel`: 120 tasks in taskgen wording whose constants fall outside taskgen's constant sets, so the model never saw
    these numbers.
  - `para`: the 120 iid tasks with the same references, reworded in a template the model never saw (for example "discard
    every value that is not greater than 5", "flip the list back to front", "Return the total of the values modulo
    16777216").
- **Training** (`train.sh`). `mlx_lm lora` with rank 8 on all layers, batch 8, 600 iterations (0.8 epoch), prompt
  masked, seed 0. The same data and iterations were used for every size.
- **Evaluation.** n=4 samples per task, temperature 0.7, top_p 0.95. pass@1 is the mean per-task pass fraction. CIs are
  95% task-bootstrap intervals. A sample passes only if its assembled net passes `genome.verify` at seed 0. A
  sound-for-FAIL prefilter (`score.refute_py`) marks a program wrong if the words' Python semantics disagree with the
  reference on an edge or random input. It never grants a pass.

## Results

pass@1 in %, n=4 samples per task, with a 95% task-bootstrap CI. d = composition depth in words (list stages plus the
reducer). Task counts: iid 120 (d1 7, d2 40, d3 73), deep 40/40/40/30/30, novel 120, para 120.

**Main table: model size at a uniform recipe** (lr 5e-5, LoRA rank 8 on all layers, batch 8; 600 iterations for 0.6B
and 1.7B, 300 for 4B, see Caveats). Each cell shows pass@1 in %, then passing samples / total samples.

| trained model | iid [CI] | iid d1/d2/d3 | deep d3 / d4 / d5 | deep d7 / d8 (beyond training) | novel constants | **paraphrase (unseen wording) [CI]** |
|---|---|---|---|---|---|---|
| Qwen3-0.6B-4bit | 100 (480/480) [100, 100] | 100/100/100 | 100 / 100 / 100 (160/160 each) | 100 / 100 (120/120 each) | 100 (480/480) | 43.3 (208/480) [35.4, 51.2] |
| Qwen3-1.7B-4bit | 99.8 (479/480) [99.4, 100] | 96.4/100/100 | 100 / 100 / 100 | 100 / 100 | 100 (480/480) | 77.7 (373/480) [70.6, 84.2] |
| Qwen3-4B-4bit | 100 (480/480) [100, 100] | 100/100/100 | 100 / 100 / 100 | 100 / 100 | 100 (480/480) | 66.7 (320/480) [59.4, 74.0] |

**Other runs**

| run | iid | deep d3/d4/d5/d7/d8 | novel | paraphrase |
|---|---|---|---|---|
| 1.7B, lr 2e-4 (**kill-rule model**, first run) | 100 (480/480) [100, 100] | 100/100/100/100/85.0 (702/720 overall) | 100 (480/480) | 20.8 (100/480) [15.0, 26.9] |
| 1.7B, lr 5e-5, **three training wordings** (A taskgen, B, C; test wording D unseen) | 99.8 (479/480) | 98.1/100/97.5/100/100 (713/720) | 98.8 (474/480) | **92.7 (445/480) [87.9, 96.5]** |
| 0.6B, lr 2e-4 (diverged: loss 4.6 -> 6.2 at iteration 25, 0.85 at the end) | 0.6 (3/480) | 0 (0/720) | 0 (0/480) | 0 (0/480) |
| Qwen3-4B-Instruct-2507, **no tuning**, vocabulary and one example in the prompt | 71.5 (343/480) [63.7, 79.0]; d1/d2/d3 85.7/70.6/70.5 | not run | not run | 52.7 (253/480) [44.2, 61.7] |

**Baselines on the same 120 iid tasks, by depth**

| author | what it writes | d1 | d2 | d3 | all |
|---|---|---|---|---|---|
| native_v1 (Qwen3-4B-Instruct-2507, LoRA on Luna nets), n=8 | the whole net | 62.5 [35.7, 87.5] | 24.4 [15.6, 34.4] | 4.3 [2.1, 7.0] | 14.4 [9.9, 19.1] |
| stage model 1.7B (lr 2e-4), n=4 | stage words | 100 (28/28) | 100 (160/160) | 100 (292/292) | 100 (480/480); paired delta **+85.6 [+80.9, +90.1]** |
| no-tuning 4B-Instruct plus vocabulary, n=4 | stage words | 85.7 | 70.6 | 70.5 | 71.5 (343/480); paired +57.1 [+47.8, +65.7] |
| Luna Pro API (frozen author, primer and linter, several attempts), taskgen train pipeline+reduce, **not the same tasks** | the whole net | first attempt 71.8 (28/39); accepted 97.4 | 51.3 (100/195); 94.4 | 39.1 (104/266); 91.4 | first attempt 46.4 (232/500); accepted 93.0 (465/500) |

Luna by depth comes from the `runs/datagen/native/seed0` state files (the first attempt and the final acceptance). The
1-, 2- and 3-stage rows were never separated before.

**KILL RULE: NOT HIT.** The 1.7B stage-emitting model scores 100% on the covered iid tasks (120/120 covered, 480/480
samples; the rule needed at least 50%). It beats the plain 4B by +85.6 points [80.9, 90.1] paired (the rule needed at
least 20). Every size and recipe that converged clears both bars. Composition depth no longer matters up to 5 stages:
100% at d3, d4 and d5 for every converged model. At 7 and 8 stages, longer than any training pipeline, the lr 5e-5
models stay at 100%. The lr 2e-4 1.7B model drops to 85% at d8 because it stops after 6 or 7 lines, the length it
was trained on. Fresh-seed audit: 40 randomly chosen passing (task, program) pairs from iid and deep all pass
`genome.verify` at seed 1 (`runs/exp15/audit_seed1.json`).

**Size.** 0.6B is enough on templated text. Size and learning rate matter only for **reading unseen wording**: 43% at
0.6B, 78% at 1.7B and 67% at 4B (lr 5e-5). This is not monotone in size, and the 4B run had half the steps. The 4B
paraphrase failures are mostly unseen surface forms echoed as words (`skip k` 53 samples, a stage after `reduce` 28,
`reduce prefixsum`). At 1.7B, the harsh lr 2e-4 fine-tune drops it to 21%. Putting three
wordings in training raises it to 93% at the same size. The remaining paraphrase errors are the unseen number form
"modulo 16777216" (written instead of 2^24, so the model emits `mod 16777216` as an extra word) and the double negation
"discard every value that is not greater than k", which it reads as `filter lt k`. Single-wording models get 0% on
negated filters ("throw away the odd values" should give `filter even`) and on `dedup` in the new wording
(`pass_vs_size.svg`).

**Zero-shot control.** An untuned Qwen3-4B-Instruct-2507, given the vocabulary and one example in the prompt, reaches
71.5% on iid and 52.7% on para. Its errors are mostly format: `last`, `first`, `min` or `count` written without
`reduce` (84 of 480 iid samples do not parse). So pretraining alone reads the language fairly well, and fine-tuning
mostly teaches the format and the exact template mapping. On unseen wording, the single-template fine-tunes land at
43-78%, near the untuned model's 53%. Only wording diversity (93%) is clearly better than the untuned model.

**Cost of the assembled nets.** On the 45 iid tasks where native_v1 had a passing net, the assembled net takes a median
1.15x the interactions of native_v1's best passing net. The range is 0.67x to 3.2x, with three outliers (56x, 67x and
218x). All three are `sort` followed by `reduce max|min|last`: the word program really sorts, with an O(n^2) insertion
sort, where native_v1 just computed the max or min. The templates are generic and nothing is fused across stages. So
factorization buys correctness, not speed. A peephole rewrite (sort then max is max) is an easy win. Exp9-style call fusion (inlining) is the obvious next pass.

## What the model is actually learning (honest discussion)

1. **Here, the task is parsing, and a regex solves it.** Taskgen builds each description from the same stage objects
   the vocabulary mirrors, one sentence per stage. `exp13.truth`, a regex parser of about 100 lines, needs no learning at all. It
   gets 100% on iid, deep and novel. It cannot read para: it finds no stage lines, so it returns the identity program
   or raises. On templated text the fine-tuned model has
   learned to be that parser. It maps a sentence to a word, copies the constants (100% on constants it never saw, so it
   copies them rather than memorizing a set of values) and keeps the order. The depth cliff of swing 17 disappears **by
   construction**. Composition is now the glue's job: one line per stage, and the verified templates carry all the
   wiring and recursion. Swing 17's diagnosis still holds: when structure is taken out of the model's output, a very
   small model is enough.
2. **Reading language is the part that needs a model.** On the unseen wording, the single-template models fall to
   21-78%. They map surface phrases to words and do not reason about negation. A modest amount of variety in the
   wording (three templates) brings a 1.7B model to 93%. Caveat: I (an agent) wrote the B, C and D wordings, so they
   share an author and some phrasing habits. D is unseen but not independent, and real user text would be harder.
3. **The vocabulary was designed, not grown.** The 24 words (`exp13/words.py`: 12 list stages and 12 reducers, with 8 expression and 6 predicate
   forms for the holes) were written by hand
   by an agent to match taskgen's stage list one to one. Coverage is therefore 100% on pipeline and reduce and 0% on 10
   of 14 taskgen families: sortlike, arith, rangefn, treefold, zip2, group, treemap, treetrav and both recon families
   (the types are trees, tuples and triples). Several of those could be written as sequences of the existing words
   (sortlike: `sort`, `reverse`, `take k`), but the test descriptions are not phrased in stages. So this swing shows
   the second half of the claim: given verified words, a small model can compose them reliably and the glue makes
   the result correct. It does not show the first half.
4. **What remains for "a language grown from verified words":**
   - (a) Words that are **induced** rather than designed. The candidates: the `induce.py` subnet miner, and exp13's
     enumerator for hole filling, turned into a word-proposal loop with verification as the gate.
   - (b) A test whose descriptions are **not generated from the vocabulary's own stage list**: natural statements,
     the 200-program corpus, and the holdout families.
   - (c) **Words added after training** used in context (vocabulary in the prompt, as in the zero-shot control).
   - (d) Non-list types and non-linear dataflow (zip, trees, graphs), where "compose by sequence" is no longer enough
     and the glue needs a typed port checker (swing 23).

## Caveats

- **LR 2e-4 was unstable.** 0.6B diverged, the first 4B run spiked to loss 6.5 at iteration 50, and a wording-augmented
  1.7B run stalled at 0.8. The 1.7B lr 2e-4 run converged. The kill-rule claim rests on it, and the lr 5e-5 1.7B
  confirms it (99.8%).
- **4B iterations.** The 600-iteration lr 5e-5 4B run was killed externally at iteration ~250 with no error in its log.
  Its loss was already 0.000 by iteration 100. It was rerun at 300 iterations to fit the time box, so the 4B row saw
  half the steps.
- **Baselines.** native_v1 used Qwen3-4B-Instruct-2507; the stage models use the base Qwen3 checkpoints. The Luna
  numbers are on different (training-distribution) tasks with the primer, the linter and retries.
- n=4 samples per task. The 100% cells have zero-width bootstrap CIs; the Wilson 95% lower bound for 480/480 samples is
  99.2%.

