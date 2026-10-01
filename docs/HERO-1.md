# HERO-1: an English seating rule becomes a verified program that seats 34 or 100,000 guests (2026-09-30)

Swing 28. Order of writing: section 1 (kill rule and protocol) and the frozen test set were committed to disk before any model was trained or
sampled; section 1b (a second, external test set) was added after the first results and before that set was run; everything else was filled in after the runs.

## Summary (plain language)

**Verdict: the kill rule is not hit. The hero works on independently worded rules, with a caveat about what is and is not verified.**

- A tiny local model (Qwen3-1.7B, 4-bit, LoRA-tuned on 9,000 synthetic sentences) turns a seating rule into a 1-4 line program. On 72 hand-written policies in six voices it reads them
  correctly **98.6%** of the time (355/360 samples; 99.0% over 1,440 samples; greedy 72/72), including 12 policies whose stage combination was never in training (96.7%). On a second set written by
  a different author (72 policies, 14 voices, kept frozen) it scores **90.6%** (326/360). The bar was 80%.
- The program runs on a verified interaction net (`genome.verify`, seeds 0-2 pass, plus 5,000 extra random cases). Its output equals the Python reference at 1,000, 10,000 and 100,000 synthetic guests, with 0 rule violations;
  100,000 guests take 1.5-3 s on the arm64 C runtime (work linear, depth linear and not parallel: about 65 rounds per guest).
- Against a prompted local chatbot on the real 34-guest chart: the untuned Qwen3-4B-Instruct produced **0 fully clean answers in 400**, broke a policy-specific rule in 88% of parsed answers, missed or duplicated a guest in 91%, and gave 17.7 different answers per policy in 20 samples. The pipeline gave 0
  violations, no missing guests, and 1 answer per policy. A 30B-A3B local model is better but still breaks a rule in 73% of answers.
- What "exact" does and does not cover: the net is exact for the program it is given. When the model misreads a sentence (about 1% on set 1, 9% on set 2) the answer is a perfect arrangement for the wrong rules; showcase rule 4 is an example.
  Requests outside the six words (18 tried) are rejected by the parser in 57% of samples and silently mis-executed in 43%.

## 1. Kill rule and protocol (frozen before running)

**Question.** Can a plain-English seating rule be turned by a tiny local model into a short stage program that a verified net
executes exactly, and does that survive rules worded independently of the training templates?

**Test set (frozen).** `data/hero/policies_test.json`, sha256
`a758fb81b7ce2cb07379104f4d0d5d28726139433e8e7cca447426ffe278a480`. 72 policies I wrote by hand before any model existed,
6 voices x 12 (terse, formal, chatty, negative-first, list style, wedding-planner). None was produced by the training
generator; the file was not edited after freezing (script `genome/hero1/make_test_set.py` refuses to overwrite it). Each
policy has a gold stage program written by hand at the same time. 12 policies (two for each of six held-out signatures, listed as `heldout_combo`
H1-H6) use a combination of stage words whose exact combination is EXCLUDED from the training set:
H1 {together company, apart, order}, H2 {size, together category, limit}, H3 {limit, apart, order},
H4 {size, together company, together category, order}, H5 {together category, apart}, H6 {size, limit, apart, order}.

**Pipeline under test.** policy sentence -> LoRA-tuned Qwen3-1.7B (MLX) -> stage program (strict parser) -> compiled rule table and
guest sequence -> the verified sectioner net (`genome/hero1/sectioner.py`) run on the pinned HVM2 executor -> section per guest.

**A sample passes** iff (1) its text parses under the strict parser, and (2) on ALL FOUR guest lists - the real 34-guest luncheon
chart and the 3 synthetic lists (`genome/hero1/guests.py` `AGREE_LISTS`: n = 48/80/120, seeds 101/202/303, mixes
balanced/gov_heavy/tech_heavy, every category present) - the net's section assignment, decoded by the same executor and type
decoder that `genome.verify` uses, equals the reference assignment computed in pure Python from the GOLD program of that policy.
(Equal assignments = same partition into numbered sections; the reference numbers sections in seating order.) Zero rule
violations of the gold rules by the assignment is checked separately with an independent checker (`lang.violations`).
Exact text match to the gold program is reported as a secondary number.

**pass@1** of a policy = the fraction of n = 5 samples (temperature 0.7, top_p 0.95, one seed) that pass. The headline number is
the mean over the 72 policies (equivalently the expected pass rate of one sample). Greedy decoding (temperature 0) is reported next to it.
Intervals are 95% policy-level bootstrap.

**KILL RULE.** Headline pass@1 over the 72 independent policies: at least 80% = the hero works on independent wording.
60% to under 80% = PARTIAL, and I report which wording failures dominate. Under 60% = KILLED.
Secondary (reported, not part of the rule): the 12 held-out-combination policies alone, each voice alone, exact-text match.

**Chatbot baseline.** 20 of the 72 policies (selection fixed here: the first 3 policies of each voice, ids `xxx01`-`xxx03`, = 18, plus the two
held-out policies `ter11` and `for11`) are given to the untuned
local Qwen3-4B-Instruct-2507 (MLX, 4-bit) with the real 34 guests listed as `G01..G34` plus company and category only (no names),
20 samples per policy at temperature 0.7 (400 samples), asked for a JSON list of sections. Reported: fraction of samples with at
least one violation of a stated rule (same checker as the pipeline), fraction with any guest missing or duplicated,
distinct answers per policy out of 20. The pipeline's counterpart: violation count on the same 20 policies (must be 0 by construction; verified)
and distinct answers (must be 1).

**Scope of "verified".** The sectioner is one net, verified by `genome.verify` (hidden suite: edge cases, random cases at authoring
sizes and 16x, exhaustive small sweep) on seeds 0-2. The stage program compiles to DATA for that net (rule table + guest
sequence), so the model does not write or change any net. Sorting guests into the sequence (grouping companies, priority order)
is done by host code, not the net.

### 1b. Second, externally authored test set (added after the first results, before it was run)

The first results (section 3) were strong, and the first test set was written by the same agent that designed the vocabulary. So a
separate subagent that saw neither the training data nor test set 1 wrote a second set: `data/hero/policies_test2.json`, sha256
`19c2df3d94110b9d62b5f310feee73b1c956b4ac43cb6d26f324689ef9fc5ca9`, frozen as delivered (I checked only that every gold program parses; nothing was edited).
It holds 72 IN-SCOPE policies (14 voices, 1-4 rules each, gold programs written by the subagent from a written spec of the six words) and
18 OUT-OF-SCOPE requests that no program can express (gold null). Same pass criterion as section 1 (four guest lists, reference from the subagent's gold),
same model, n = 5 samples at T = 0.7 and greedy. It is reported as a supplement; the kill-rule verdict is the first set's, as fixed above.
For the 18 out-of-scope requests there is no pass; I report what the system does with them.

## 2. What was built

Code is in `genome/hero1/`, outputs in `runs/hero1/`, the frozen test set in `data/hero/policies_test.json`. Local compute only (MLX
venv, pinned HVM2). No paid API.

### 2.1 The seating stage vocabulary (6 words)

Guests carry only the printed company (or none) and the coarse category of `data/hero/luncheon.json`.

| word | meaning (a HOST rule in a game, not a claim about any guest) | maps to |
|---|---|---|
| `size N` | at most N guests per section (1-6, default 6) | capacity |
| `together company` | guests of one company sit in one section (as few sections as the company can fit in) | affinity cluster |
| `together CAT` | all guests of a category sit together (same rule) | affinity cluster |
| `limit CAT.. K` | at most K guests from the listed categories, counted together, per section | per-category maximum (K=1 is "no two of ...") |
| `apart A B` | no guest of A shares a section with a guest of B | must-not-link (class level) |
| `order CAT..` | listed categories are seated first, in this order (lower section numbers) | priority order |

Sections are contiguous runs of the seating sequence, so contiguous runs of seats when the sequence is laid around the table
(left row 0..16, then right row 16..0). "Section captain" is not a word here: the section number is the identifier.

### 2.2 The verified net (`genome/hero1/sectioner.py`) and why exp18 was not reused

Semantics (module doc of `genome/hero1/lang.py`, reference `ref_sections`): host code builds the guest SEQUENCE (units for
`together`, sorted by priority rank); the net then runs a next-fit pass over it. State = (section, size, one counter pair per
rule). A guest (category c, s) - s is the unit size on the first member of a unit and 0 on the others - joins the current section
iff `size + max(s,1) <= cap` and no rule (mask A, mask B, k) is broken (`c in A and (a + t > k or b > 0)` or `c in B and a > 0`);
otherwise a new section is opened. So a unit that fits nowhere whole is filled into fresh sections one chunk at a time. A `limit`
word is the rule (mask, 0, K); an `apart` word is (maskA, maskB, infinity). One rule form covers both, and the capacity is a
separate register.

Net (HVM2 interaction net, 14 small definitions): the walker `st` rebuilds the rule-counter list twice while it scans it
(once with the guest admitted to the current section, once with a new section opened first) and computes the fit flag; the step
keeps one list and erases the other. Cost: about 360 interactions and 65 rounds of depth per guest for the scale policy P1 (3 rule cells)
in section 4; work is linear, depth is linear (the pass is sequential by construction).

`genome.verify` (hidden suite `v2`: 11 edge cases, 24 random at authoring sizes 4-32 guests, 6 random at 128 and 320 guests compared by digest, 60
exhaustive-small inputs) on the corpus-style Program `hero1_sectioner` (reference = `ref_sections`, registered in
`genome/hero1/sectioner.py`): **seeds 0, 1 and 2 all pass, 101/101 cases each** (`runs/hero1/verify_kernel.log`). Extra stress
outside the suite: 3,000 random inputs of up to 300 guests, 3,000/3,000 equal to the reference (`genome/hero1/stress.py`).
Independent semantics check: for 600 random policies over random guest lists the reference assignment has 0 violations under a
separately written rule checker (`genome/hero1/selftest.py`, `lang.violations`); the net equals the reference on the 120 of
them it was run on.

Why not exp18's `t5_conflict_greedy_cap`: (1) it only knows pairwise must-not-link, so "at most 2 government officials per
section" cannot be written; (2) `apart ai_lab big_tech` on n guests needs |A|x|B| pairs (about 1e8 at n = 100,000 with the mix used below), and
its work is O(candidates x |mnl|), so it was verified only up to n = 144; (3) it wants a scored candidate list, which a rule sentence
does not supply. What is reused is the recipe: verified kernel, parameters as data, fixed glue, `genome.verify` as the judge.
The sectioner is a new template; it is not a claim about exp18's nets.

### 2.3 Program, glue and the honest boundary

The model emits the stage program. `genome/hero1/lang.py` parses it strictly and compiles it to (cap, rule table) and a host
step orders guests into the sequence (grouping companies, priority rank). The net does the rule checking and the sectioning.
The sorting/grouping is host Python (O(n log n), 0.05 s at 10,000 guests), not a net, and it is shared by the reference, so
exactness at scale means "net = Python reference given the same sequence"; the rule checker (independent code) then confirms
0 violations of cap, limit, apart, together and order on the output.

### 2.4 Training set and model

`genome/hero1/gen_train.py`: 9,000 training and 200 validation (policy text -> program) pairs. Policies are sampled over all
combinations of the six words, EXCLUDING the six held-out signatures H1-H6 (58 signatures occur; every held-out signature is missing,
its individual words all occur). Texts come from a template engine over two phrase banks: 540 templates in 10 voices written by a
separate subagent that never saw the test set (`genome/hero1/phrasebank_agent.json`; plus 7 x 16-18 category noun phrases, 50 openers,
36 joiners, 29 closers) and a small plain core bank of mine (`gen_train.py`). Overlap with the frozen test wording
(`runs/hero1/overlap.json`): 0 of 72 test texts occur in training; the share of test n-grams that occur anywhere in the training texts
is 95% (words), 76% (bigrams), 50% (trigrams), 27% (4-grams), 13% (5-grams); median nearest-neighbour trigram Jaccard 0.11.
Model: Qwen3-1.7B (MLX 4-bit) + LoRA rank 8 on all layers, batch 8, lr 5e-5, 1,200 iterations (about 1.1 epochs), prompt masked,
seed 0 (`genome/hero1/train.sh`). One recipe, chosen before the test set was sampled; nothing was tuned against the test set.

## 3. Result on the frozen test set (section 1 protocol)

**Verdict against the kill rule: PASS.** Headline pass@1 = **98.6%** (355/360 samples over 72 policies; policy-level bootstrap 95% interval
96.4% to 100%), against a bar of 80%. Greedy decoding passes 72/72 policies (100%). The threshold for "partial" (60-80%) and "kill" (below 60%) was
not approached. The exact program text also equals the gold program in every one of the 355 passing samples (no sample passed with a different
but behaviourally equal program), so the behavioural criterion did not inflate the number.

Model: Qwen3-1.7B-4bit + LoRA (`adapters/hero1_1p7b`), trained once (1,200 iterations, final validation loss 0.009). On its own 200 held-back
validation policies (same template engine as training) greedy decoding gives 196/200 exact programs.

| test set 1, T=0.7, n=5 | policies | passed samples | pass@1 [95% CI] | exact program text |
|---|---|---|---|---|
| all policies | 72 | 355/360 | 98.6% [96.4, 100.0] | 98.6% |
| seen stage combination | 60 | 297/300 | 99.0% [97.0, 100.0] | 99.0% |
| held-out combination (H1-H6) | 12 | 58/60 | 96.7% [90.0, 100.0] | 96.7% |
| voice: chatty | 12 | 58/60 | 96.7% [90.0, 100.0] | 96.7% |
| voice: formal | 12 | 60/60 | 100.0% [100.0, 100.0] | 100.0% |
| voice: list | 12 | 60/60 | 100.0% [100.0, 100.0] | 100.0% |
| voice: negative | 12 | 60/60 | 100.0% [100.0, 100.0] | 100.0% |
| voice: terse | 12 | 60/60 | 100.0% [100.0, 100.0] | 100.0% |
| voice: wedding | 12 | 57/60 | 95.0% [85.0, 100.0] | 95.0% |
| held-out H1 | 2 | 10/10 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H2 | 2 | 8/10 | 80.0% [60.0, 100.0] | 80.0% |
| held-out H3 | 2 | 10/10 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H4 | 2 | 10/10 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H5 | 2 | 10/10 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H6 | 2 | 10/10 | 100.0% [100.0, 100.0] | 100.0% |

| test set 1, greedy | policies | passed samples | pass@1 [95% CI] | exact program text |
|---|---|---|---|---|
| all policies | 72 | 72/72 | 100.0% [100.0, 100.0] | 100.0% |
| seen stage combination | 60 | 60/60 | 100.0% [100.0, 100.0] | 100.0% |
| held-out combination (H1-H6) | 12 | 12/12 | 100.0% [100.0, 100.0] | 100.0% |
| voice: chatty | 12 | 12/12 | 100.0% [100.0, 100.0] | 100.0% |
| voice: formal | 12 | 12/12 | 100.0% [100.0, 100.0] | 100.0% |
| voice: list | 12 | 12/12 | 100.0% [100.0, 100.0] | 100.0% |
| voice: negative | 12 | 12/12 | 100.0% [100.0, 100.0] | 100.0% |
| voice: terse | 12 | 12/12 | 100.0% [100.0, 100.0] | 100.0% |
| voice: wedding | 12 | 12/12 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H1 | 2 | 2/2 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H2 | 2 | 2/2 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H3 | 2 | 2/2 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H4 | 2 | 2/2 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H5 | 2 | 2/2 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H6 | 2 | 2/2 | 100.0% [100.0, 100.0] | 100.0% |

Every one of the 360 samples parsed under the strict parser. Sampling noise at n = 5 is small: a second, larger run at n = 20 (1,440 samples) is in section 3b.

**Failures (5 of 360 samples, 2 of 72 policies).** Both are the same kind: a size rule is lost or misfiled. `cha12` (chatty, held-out combination
H2, "Sections of three, the AI lab people all sit together, and no more than one government person per section.") dropped the leading
"Sections of three" clause in 2 of 5 samples (`together ai_lab; limit government 1`). `wed10` (wedding-planner voice, "Keep every chip maker
together, no more than five to a section, and never put chips with AI labs.") read "no more than five to a section" as a per-category limit
in 3 of 5 samples (`limit chips 5` instead of `size 5`). No parse errors, no wrong category names, no wrong order sequences, no other
wording family failed. The 12 policies whose stage combination is absent from training pass 58/60 (96.7%), against 297/300 (99.0%) for
the 60 seen combinations; the one held-out failure is the `cha12` size omission. With 2 policies failing, no wording-family claim beyond
"size clauses are the weak point" is supported.

**Diagnostics of the test itself.** Gold pipeline (gold program through the net) passes 72/72 with 0 rule violations
(`genome.hero1.pipeline.judge` on gold). The four guest lists distinguish 66 different gold programs pairwise except one pair
(`size 4` versus `size 4` + `limit investor 2`, the second rule never binds on these lists), so a program that adds a non-binding rule could pass
on assignments; that is why exact text match is reported next to the pass rate (identical here).

**Control: what the tuning buys.** Same 72 policies, n = 5, T = 0.7, same judge, no tuning, the stage vocabulary and one example in the prompt
(`--vocab`): Qwen3-4B-Instruct-2507 passes 245/360 = 68.1% [57, 78] (94% of outputs parse); untuned Qwen3-1.7B outputs `none` for 336 of 360 samples and unparsable text for the rest (0/360). So a 4B instruct model can read the vocabulary but is 30 points behind the tuned 1.7B, and the tuned model is 2.3x
smaller.

### 3b. Robustness supplements on test set 1, and test set 2 (external author)

**More samples.** Same set, n = 20 samples per policy at T = 0.7 (1,440 samples, a different seed): **1,426/1,440 = 99.0% [97.5, 100]**;
the 12 held-out-combination policies 237/240 = 98.8%. The failing policies are `wed10` (11/20 pass, the same "no more than five to a
section" misfiling as `limit chips 5`), `cha12` (17/20, dropped size) and `lis04` (18/20, two samples with a corrupted category token,
`apart chips softwar...`). Files: `runs/hero1/samples/test_t07_n20.*`.

| test set 1, T=0.7, n=20 | policies | passed samples | pass@1 [95% CI] | exact program text |
|---|---|---|---|---|
| all policies | 72 | 1426/1440 | 99.0% [97.5, 100.0] | 99.0% |
| seen stage combination | 60 | 1189/1200 | 99.1% [97.4, 100.0] | 99.1% |
| held-out combination (H1-H6) | 12 | 237/240 | 98.8% [96.2, 100.0] | 98.8% |
| voice: chatty | 12 | 237/240 | 98.8% [96.2, 100.0] | 98.8% |
| voice: formal | 12 | 240/240 | 100.0% [100.0, 100.0] | 100.0% |
| voice: list | 12 | 238/240 | 99.2% [97.5, 100.0] | 99.2% |
| voice: negative | 12 | 240/240 | 100.0% [100.0, 100.0] | 100.0% |
| voice: terse | 12 | 240/240 | 100.0% [100.0, 100.0] | 100.0% |
| voice: wedding | 12 | 231/240 | 96.2% [88.8, 100.0] | 96.2% |
| held-out H1 | 2 | 40/40 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H2 | 2 | 37/40 | 92.5% [85.0, 100.0] | 92.5% |
| held-out H3 | 2 | 40/40 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H4 | 2 | 40/40 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H5 | 2 | 40/40 | 100.0% [100.0, 100.0] | 100.0% |
| held-out H6 | 2 | 40/40 | 100.0% [100.0, 100.0] | 100.0% |

**Test set 2 (section 1b).** 72 in-scope policies by a different author in 14 voices:
**326/360 = 90.6% [83.6, 96.7]** at T = 0.7, greedy 65/72 = 90.3%. Above the 80% bar, 8 points below test set 1.
The exact program text again equals the gold in every passing sample.

| test set 2, T=0.7, n=5 | policies | passed samples | pass@1 [95% CI] | exact program text |
|---|---|---|---|---|
| all policies | 72 | 326/360 | 90.6% [83.6, 96.7] | 90.6% |
| voice: assistant_instruction | 5 | 25/25 | 100.0% [100.0, 100.0] | 100.0% |
| voice: bullets | 5 | 25/25 | 100.0% [100.0, 100.0] | 100.0% |
| voice: casual_chat | 4 | 20/20 | 100.0% [100.0, 100.0] | 100.0% |
| voice: corporate_memo | 6 | 30/30 | 100.0% [100.0, 100.0] | 100.0% |
| voice: legalese | 6 | 25/30 | 83.3% [50.0, 100.0] | 83.3% |
| voice: nervous_text | 5 | 25/25 | 100.0% [100.0, 100.0] | 100.0% |
| voice: non_native | 5 | 25/25 | 100.0% [100.0, 100.0] | 100.0% |
| voice: poem | 4 | 14/20 | 70.0% [25.0, 100.0] | 70.0% |
| voice: question | 4 | 20/20 | 100.0% [100.0, 100.0] | 100.0% |
| voice: rambling | 4 | 10/20 | 50.0% [0.0, 100.0] | 50.0% |
| voice: shouty | 5 | 20/25 | 80.0% [40.0, 100.0] | 80.0% |
| voice: spoken | 6 | 30/30 | 100.0% [100.0, 100.0] | 100.0% |
| voice: teacher | 6 | 25/30 | 83.3% [50.0, 100.0] | 83.3% |
| voice: terse | 7 | 32/35 | 91.4% [74.3, 100.0] | 91.4% |

Failures concentrate in 8 policies (6 policies 0/5, `a29` 2/5, `a20` 4/5); the rest pass 5/5. What went wrong, by policy:
- **Fan-out of `apart` (a38, a63; 0/5 each).** "Keep the investors away from the model builders and away from the big platforms" needs
  `apart ai_lab investor` + `apart big_tech investor`. The model wrote `apart ai_lab big_tech` + `apart investor big_tech` (a38) or a 3-argument `apart` that the parser rejects (a63,
  "Neither AI laboratory personnel nor large-platform personnel shall be seated ... with a governmental body"). Training had only independent pair sentences.
- **`apart` versus `limit` (a49).** "The chip folks and the AI labs must be in separate sections from each other" was written `limit ai_lab chips 1`,
  a different rule (also forbids two AI labs together). Wrong reading, valid program.
- **Category paraphrase not in training (a56).** "GPU designers" was mapped to `ai_lab` instead of `chips` (5/5). (The bank had chip makers, semiconductor, silicon, chipmakers; not GPU.)
- **Truncated `order` (a72).** "the funds must be put first, ahead of the vendors" -> `order investor` (vendors dropped). The gold `order investor software_security` is
  the stronger reading of the sentence; a defender of the model can call this ambiguous. I keep the gold as delivered and count it a failure.
- **Corrupted category tokens (a20 and a57 are poems, a29 is terse).** At T = 0.7 the model sometimes writes category words that are not identifiers (`lab`, `labs`, `pool`);
  the strict parser rejects them, so they cost a pass but never run. `a57` (a three-line poem) fails 5/5 with `together company` / `together pool` hallucinated.
Voice summary: rambling 50%, poem 70%, shouty 80%, legalese/teacher 83%, everything else 91-100%. With 4-7 policies per voice these are anecdotes, not rates.

| test set 2, greedy | policies | passed samples | pass@1 [95% CI] | exact program text |
|---|---|---|---|---|
| all policies | 72 | 65/72 | 90.3% [83.3, 97.2] | 90.3% |
| voice: assistant_instruction | 5 | 5/5 | 100.0% [100.0, 100.0] | 100.0% |
| voice: bullets | 5 | 5/5 | 100.0% [100.0, 100.0] | 100.0% |
| voice: casual_chat | 4 | 4/4 | 100.0% [100.0, 100.0] | 100.0% |
| voice: corporate_memo | 6 | 6/6 | 100.0% [100.0, 100.0] | 100.0% |
| voice: legalese | 6 | 5/6 | 83.3% [50.0, 100.0] | 83.3% |
| voice: nervous_text | 5 | 5/5 | 100.0% [100.0, 100.0] | 100.0% |
| voice: non_native | 5 | 5/5 | 100.0% [100.0, 100.0] | 100.0% |
| voice: poem | 4 | 3/4 | 75.0% [25.0, 100.0] | 75.0% |
| voice: question | 4 | 4/4 | 100.0% [100.0, 100.0] | 100.0% |
| voice: rambling | 4 | 2/4 | 50.0% [0.0, 100.0] | 50.0% |
| voice: shouty | 5 | 4/5 | 80.0% [40.0, 100.0] | 80.0% |
| voice: spoken | 6 | 6/6 | 100.0% [100.0, 100.0] | 100.0% |
| voice: teacher | 6 | 5/6 | 83.3% [50.0, 100.0] | 83.3% |
| voice: terse | 7 | 6/7 | 85.7% [57.1, 100.0] | 85.7% |

**Out-of-scope requests (18, section 1b).** No pass is defined. Over 90 samples, 51 are rejected by the strict parser (words like `together nvidia microsoft`, `order company`),
and 39 are valid programs that silently do something else: e.g. "at least two AI lab guests per section" becomes `limit ai_lab 2` (an at-most rule, the
opposite direction), "try to keep investors away from the AI labs" becomes `apart ai_lab investor`, and "exactly one chip maker in every section" becomes `limit chips 1`.
The model has no way to say "this cannot be expressed". That is a product gap, not a measured failure of the kill rule (see caveats).

## 4. Scale test (hero output b)

Policies (English gloss in `genome/hero1/scale.py`): P1 = `size 5; together company; limit government 2; apart ai_lab big_tech; apart chips investor;
order ai_lab chips` (6 words, 3 rule cells) and P2 = `size 4; together company; together government; limit investor 1; apart software_security big_tech; order investor`.
Synthetic guests (`genome/hero1/guests.py`, mix "balanced": ai_lab 9%, big_tech 13%, chips 10%, software_security 12%, investor 12%, government 22%, unlabelled 22%;
government/unlabelled 65% without a printed company; company sizes 1-8, half single), seed 7. Reference = pure Python `ref_sections`
on the same sequence. "Net = reference" is a comparison of the full output list (n <= 10,000: decoded item by item on the Rust interpreter;
all sizes: two 24-bit digests of the whole list computed inside the executor on the arm64 C runtime). Rule violations are counted
by the independent checker on the reference output (cap, limit, apart, together, and the O(n log n) order-inversion count).
Depth and bare-net interactions come from the depth oracle (`physics/hvm2-depth`); wall-clock from the arm64 C runtime
(HVM2 `hvm.c`, `-O3 -mcpu=native`, 8 threads, book passed as data, exp16 driver), 3 runs per cell. The machine was shared and heavily loaded (load
average 12-35), so seconds are noisy upper-ish bounds.

| policy | guests | sections | rule violations (independent checker) | net = Python reference | depth (rounds) | interactions (bare net) | C runtime seconds (3 runs: min / median / max) | book load (gen-c serialise, s) | host prep + Python ref (s) |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 1,000 | 252 | 0 | yes (digest + full decode) | 64,782 | 359,376 | 0.03 / 0.06 / 0.08 | 0.3 | 0.02 + 0.00 |
| P1 | 10,000 | 2,551 | 0 | yes (digest + full decode) | 647,573 | 3,592,961 | 0.23 / 0.34 / 0.37 | 2.5 | 0.02 + 0.04 |
| P1 | 100,000 | 25,155 | 0 | yes (digest) | 6,475,869 | 35,926,881 | 1.62 / 3.04 / 3.07 | 36.0 | 0.61 + 0.76 |
| P2 | 1,000 | 397 | 0 | yes (digest + full decode) | 57,634 | 266,078 | 0.09 / 0.15 / 0.26 | 0.4 | 0.01 + 0.00 |
| P2 | 10,000 | 3,928 | 0 | yes (digest + full decode) | 576,194 | 2,659,821 | 0.12 / 0.35 / 0.44 | 2.8 | 0.03 + 0.06 |
| P2 | 100,000 | 39,448 | 0 | yes (digest) | 5,761,574 | 26,598,321 | 1.51 / 1.54 / 2.03 | 24.3 | 0.54 + 0.36 |

Reading: exact at every size, 0 violations, work linear (about 360 interactions per guest for P1, 266 for P2, bare net), depth linear (about 65 and 58
rounds per guest: next-fit is sequential by definition, so this net gives no depth speed-up; a 100,000-guest chart costs 6.5 million dependent rounds). Wall-clock
on the C runtime is 1.5-3 s for 100,000 guests. That excludes `hvm gen-c` serialising the book with its 100,000-guest input (20-38 s at 100k, the same
harness overhead as swing 20), and host prep and the Python reference (0.3-1.0 s each at 100k).

## 5. Chatbot baseline (rule adherence)

Setup as fixed in section 1: 20 test policies (ids `xxx01`-`xxx03` of each voice, `ter11`, `for11`), the real 34 guests listed as `G01`..`G34` with
company and category only (`genome/hero1/baseline.py`), the untuned local Qwen3-4B-Instruct-2507 (MLX 4-bit) asked for a JSON list of sections,
20 samples per policy at T = 0.7, top_p 0.95 = 400 samples, one seed. A sample "violates" if the independent checker (the same one used for the pipeline;
`lang.violations`) finds any broken cap, limit, apart, together or order rule among the guests it placed. The checker counts the default size-6 cap
(stated in the prompt) as a rule; the second violation column leaves it out unless the policy sets a size. "Bad cover" = any guest missing, listed twice or invented.

| system (400 samples each) | samples | unparsable | violates a stated rule | violates a policy-specific rule (no default cap) | a guest missing, duplicated or invented | fully clean sample | distinct answers per policy | distinct partitions per policy |
|---|---|---|---|---|---|---|---|---|
| Qwen3-4B-Instruct-2507, direct answer (the specified baseline) | 400 | 3 | 392/397 (99%) | 349/397 (88%) | 360/397 (91%) | 0/400 | 17.7 / 20 | 17.6 / 20 |
| Qwen3-30B-A3B-Instruct-2507, direct answer (extra) | 400 | 1 | 292/399 (73%) | 198/399 (50%) | 287/399 (72%) | 19/400 | 12.7 / 20 | 11.6 / 20 |
| **HERO-1 pipeline** (tuned 1.7B -> program -> net) | 400 | 0 | **0/400 (0%)** of the stated rules, **0/400** of the emitted program's rules | 0/400 | **0/400** (the net returns exactly one section for each of the 34 guests) | 400/400 | **1.0 / 20** | 1.0 / 20 |

- The chatbot is not merely inexact, it does not keep the books: the 4B answer omits on average 1.0 guests and lists 3.1 twice; 360 of 397 parsed answers have at least one
  guest missing, duplicated or invented. Cap (6 or the stated size) is broken in 333 samples, `apart` in 93, `limit` in 119, `order` in 79, `together` in 51. Not one of the 400 answers is clean, and the 20 policies
  have 17.7 distinct answers each out of 20 samples.
- The larger local model (Qwen3-30B-A3B-Instruct-2507, 4-bit, same prompt and samples, run as an extra) is better and still not usable: 73% of its answers break a stated rule, 72% miss or duplicate a guest, 19/400 answers are clean
  (3 of 20 policies produce any clean sample), 12.7 distinct answers per policy. It breaks `together` (1 sample) and `apart` (9) least, `limit` (118) and the size cap (234) most.
- A reasoning variant (extra, partial): the same 4B model told to think step by step and give the JSON last, 4 samples for each of the first 10 policies (40 samples, `runs/hero1/baseline4b_cot_*`; stopped after 10 of 20 policies for time). Within a 4,000-token budget
  36 of the 40 replies never reached a parseable answer (the reasoning about 34 guests runs past the budget); the 4 that did all broke the size cap, one also broke `apart`, and two missed or duplicated a guest. So step-by-step thinking at this size and this budget
  does not rescue the direct approach, but this run is too small and too truncated to say more.
- Pipeline side (`genome/hero1/compare.py`, `runs/hero1/pipeline_vs_chatbot.json`): the same 20 policies, 20 samples each at T = 0.7 from the tuned model. All 400 programs pass the 4-list agreement test, 400/400 give
  0 violations of the stated (gold) rules, 0 violations of their own emitted rules, and re-running each net gives an identical assignment (400/400). Each policy yields exactly 1 distinct program and 1 distinct assignment across its 20 samples.
  Caution: these 20 policies are among the easiest of the 72 (the two policies the model sometimes misreads, `cha12` and `wed10`, are not in this subset). Over all 72 policies the pipeline passes 99.0%; a misread rule
  still executes exactly and yields a valid, rule-following arrangement for the WRONG rule set (see `show4` in section 6). Determinism and zero violations hold for the program, not for the reading of the English.

Reading: "0 violations" for the pipeline is by construction of the net plus checker (both verified), and it is measured against the rules the program states; the interesting quantity is how often the
sentence is read correctly (99.0% and 90.6% on the two test sets). The chatbot fails at the bookkeeping that the net does exactly. Not measured (no paid APIs allowed): a frontier chat model,
which would very likely do better than a 4B or 30B-A3B local model on the bookkeeping.

## 6. Showcase on the real 34-guest chart and the cost of authoring (hero outputs a and c)

`runs/hero1/showcase.json` (script `genome/hero1/showcase.py`): five plain-English rules, written after test set 1 was frozen and not part of either test set,
run through the tuned model (greedy) -> program -> the sectioner net on the real luncheon chart. For each: the emitted program, the section
assignment per guest (with the new seat on the walk around the table: left row 0..16, then right row 16..0, a section = a contiguous run of that walk), rule violations of the emitted
rules and of the stated (gold) rules, and the violation count of the POSTED arrangement under the stated rules (the posted chart walked the same way and cut into consecutive blocks of the section size). These are host rules in a game; nothing in
them says anything about a guest.

| # | rule (English) | program emitted (greedy) | = gold | sections | violations of stated rules: pipeline | violations of stated rules: posted chart (by kind) |
|---|---|---|---|---|---|---|
| 1 | Keep colleagues together, sections of at most four, and never put two government officials in the same section. | `size 4; together company; limit government 1` | yes | 10 | 0 | 5 (limit 3, together 2) |
| 2 | AI labs and big tech go in separate sections, chip makers get seated first, and no section bigger than five. | `size 5; apart ai_lab big_tech; order chips` | yes | 7 | 0 | 79 (order 79) |
| 3 | Seat all the investors together, keep sections to three guests, and keep the AI labs away from the chip makers. | `size 3; together investor; apart ai_lab chips` | yes | 13 | 0 | 3 (apart 1, together 2) |
| 4 | At most two government officials per section, software and security firms together, colleagues together, and investors first. | `limit government software_security investor 2` | **no** (gold: `limit government 2; together software_security; together company; order investor`) | 8 | **29** (together 3, order 26); its own emitted rules: 0 | 31 (together 4, order 27) |
| 5 | Pairs only, please. Big tech before AI labs, and never two investors in one section. | `size 2; limit investor 1; order big_tech ai_lab` | yes | 17 | 0 | 115 (order 115) |

Four of five programs are the intended ones and their arrangements have 0 violations. In the fourth the model fused the first two clauses of a four-rule sentence into one wrong `limit`;
the net ran it exactly (0 violations of what it was told, deterministic on rerun) but that arrangement breaks 29 of the host's stated rules (the same file
also stores the arrangement of the correct program, 0 violations). This is why the program is worth printing: it is 1-4 lines a host can read before the chart is used. The `order` counts are pair counts (each
guest of a non-priority category seated ahead of a priority guest counts once per priority guest), so they run large for chart-wide priority rules; the posted chart was not designed for any of these rules, so its
counts show what the metric measures, not a fault of the chart. Every net run is deterministic (rerun identical 5/5) and costs about 5,900 interactions on 34 guests.

**Cost to author the program** (single request, greedy, this shared machine, `runs/hero1/latency.json`; one warm-up excluded):

| what writes the answer | prompt tokens | generated tokens | wall-clock (greedy, per request) |
|---|---|---|---|
| tuned Qwen3-1.7B: policy -> 1-4 line program (mean of the 5 showcase policies) | 71 | 13 | 1.1 s |
| untuned Qwen3-4B-Instruct chatbot: policy + 34 guests -> section assignment (same 5 policies) | 494 | 184 | 4.9 s |
| the sectioner net running the program on 34 guests | - | - | 0.05 s (about 5,900 interactions) |

Per program (tokens out / seconds): show1: 13/1.8 s; show2: 15/1.0 s; show3: 14/2.7 s; show4: 8/0.6 s; show5: 16/1.9 s (first pass, `authoring.json`), show1: 13/1.6 s; show2: 15/1.8 s; show3: 14/0.7 s; show4: 8/0.5 s; show5: 16/0.9 s (second pass, `latency.json`). Timings vary 2-3x run to run on this shared machine; token counts do not.

The pipeline's authoring cost does not depend on the number of guests: the program is 1-4 lines (8-16 generated tokens) whether the chart has 34 or 100,000 guests. The chatbot's cost is proportional to the guests (the answer lists them all);
at 100,000 guests a direct answer would need roughly 1.7 million input and output tokens (estimated from the 34-guest counts: about 11 to read and 6 to write per guest), beyond these models' context. Net execution adds 0.05 s on 34 guests and 1.5-3 s on 100,000.

## 7. Failure taxonomy (all sampled programs)

| kind | where | count | example |
|---|---|---|---|
| clause dropped (size) | test 1: `cha12` 2/5 (n=20: 3/20) | 5 of 360 samples | "Sections of three, ..." lost at the start of a chatty sentence |
| size filed as a category limit | test 1: `wed10` 3/5 (n=20: 9/20) | 3 of 360 | "no more than five to a section" -> `limit chips 5` |
| fan-out: one entity apart from two others | test 2: a38, a63 | 10 of 360 | "away from A and away from B" -> wrong pair or 3-argument `apart` |
| `apart` read as `limit ... 1` | test 2: a49 | 5 of 360 | "must be in separate sections from each other" -> `limit ai_lab chips 1` |
| unseen category paraphrase | test 2: a56 | 5 of 360 | "GPU designers" -> `ai_lab` |
| truncated `order` sequence | test 2: a72 (arguably ambiguous gold) | 5 of 360 | "funds first, ahead of the vendors" -> `order investor` |
| corrupted category token / hallucinated word (parser rejects) | test 2 poem/terse voices (a20, a29, a57), test 1 `lis04` | 9 of 360 (test 2) + 2 of 1,440 (test 1, n=20) | `limit big_tech lab 1`, `together pool` |
| out-of-scope request silently mapped to a wrong program | test 2 out-of-scope, 39 of 90 | 39 | "at least two AI lab guests" -> `limit ai_lab 2` |

(`runs/hero1/samples/*.taxonomy.json` has the machine counts; the table groups them by cause.) What did NOT fail: no wording family collapsed; negation ("never", "don't", "no more than"), lists and
bullets, numbers as words and digits, fan-in of several categories into one `limit`, and combinations never seen in training are read correctly; the 12 held-out combinations pass at 96.7% (n = 5) and 98.8% (n = 20).
The dominant weakness is one that looks like data coverage: whatever the training templates never showed (fan-out, GPU, poem) is where the model breaks, and the gain from wording diversity is the same lesson as swing 21.

## 8. Caveats (read these before quoting a number)

1. **Same author for vocabulary and test set 1.** I designed the six words, the semantics, and wrote the 72 policies knowing what the words can say. All 72 are in scope by construction. Test set 2 (a subagent who saw a
   written spec of the six words, not the code or data) removes the shared-author effect and drops the pass rate from 98.6% to 90.6%; 8 points is the price of independent wording, not a rounding error. The real question for a product
   (what hosts actually say) is not answered by either set; 18 realistic out-of-scope requests all fail (silently in 39 of 90 samples).
2. **Training wording is partly mine.** One phrase bank came from a separate subagent that never saw the test sets; the small core bank is mine. The overlap diagnostics (0/72 exact, 27% of test 4-grams occur in training)
   show the sentences are new, not that phrasing habits are unshared. Test set 2's wording is the cleaner evidence.
3. **The behavioural pass criterion can pass a wrong program that adds a non-binding rule.** It did not happen here (exact text equals the pass rate in every table), and the four lists
   separate all 66 distinct gold programs of test set 1 from each other except one pair.
4. **"Verified" means the net, not the reading.** The sectioner is exact (hidden suite seeds 0-2, 3,000 + 2,000 extra random cases, scale digests) and the checker finds no violations of the rules the program states.
   If the model misreads the sentence the arrangement is a perfect answer to the wrong rules (`show4`). The parser catches malformed programs, not wrong ones. Print the program.
5. **Net and reference are related.** The reference and the net implement one written semantics (`lang.py`), and the same host code builds the guest sequence. What is independent: the violation checker (set-based, different algorithm),
   the 4-list comparison against the gold program, and the hidden suite's random/exhaustive inputs. The semantics itself is a design choice (next-fit, units, rank sort), not a proven-optimal seating.
6. **Not a parallelism result.** The sectioner is sequential by definition: depth 65 rounds per guest (6.5 million at 100,000). Work is linear and the C runtime is fast (1.5-3 s for 100,000), but the depth does not shrink with cores.
   Sorting and grouping are host Python (under 1 s at 100k), not a net. The 20-38 s at 100k to serialise the book is harness overhead (`hvm gen-c`), not runtime.
7. **Scale inputs are synthetic** with a plausible mix (not a real event's roster); wall-clock is from a machine at load average 12-35 (other agents), 3 runs per cell.
8. **The chatbot baseline is a 4B non-reasoning model, plus a 30B-A3B extra.** A frontier chat model was not tested (no paid APIs). The chatbot prompt is mine; a better prompt (or reasoning) helps
   (see the extra above) but the bookkeeping failure rate is high enough that the qualitative result should survive.
9. **Sections are contiguous runs of a walk around the table;** the two ends of the walk (the head and foot of the long table) are treated as adjacent. The posted chart's "sections" for the violation counts are my cut into blocks of the section size, not something the chart states.
10. **Small n.** 72 policies x 5 samples; per-voice cells have 12 (set 1) or 4-7 (set 2) policies. One policy (`wed10`) accounts for 3 of 5 failing samples on set 1; `cha12` for the other 2.
11. **One trained model, one recipe.** No comparison of 0.6B or 4B, no ablation of training-data diversity; the claim about coverage in section 7 is a diagnosis from the failures, not an ablation.

## 9. Files and how to reproduce

| what | where |
|---|---|
| language, semantics, reference, rule checker | `genome/hero1/lang.py` |
| verified net + corpus-style Program (hidden suite), seeds 0-2 log | `genome/hero1/sectioner.py`, `runs/hero1/verify_kernel.log` (`python3 -m genome.hero1.sectioner 0 1 2`) |
| extra kernel and semantics tests | `genome/hero1/stress.py`, `genome/hero1/selftest.py` |
| synthetic guests, pipeline, 4-list judge | `genome/hero1/guests.py`, `genome/hero1/pipeline.py` |
| frozen test sets and writers | `data/hero/policies_test.json` (`genome/hero1/make_test_set.py`), `data/hero/policies_test2.json` (subagent) |
| training data generator, phrase banks, data | `genome/hero1/gen_train.py`, `genome/hero1/phrasebank_agent.json`, `runs/hero1/data/`, `runs/hero1/train_meta.json`, `runs/hero1/overlap.json` |
| training, adapter, log | `genome/hero1/train.sh`, `adapters/hero1_1p7b/`, `runs/hero1/train_1p7b.log` |
| sampling, judging, taxonomy | `genome/hero1/sample.py`, `evaluate.py`, `taxonomy.py`, `report.py`; `runs/hero1/samples/*` (samples, `.scored.json`, `.eval.txt`, `.taxonomy.json`) |
| chatbot baseline and the pipeline comparison | `genome/hero1/baseline.py`, `compare.py`; `runs/hero1/baseline*_samples.json`, `baseline*_scored.json`, `pipeline_vs_chatbot.json` |
| showcase (a) and authoring cost (c) | `genome/hero1/showcase.py`, `latency.py`; `runs/hero1/showcase.json`, `authoring.json`, `latency.json` |
| scale test (b) | `genome/hero1/scale.py`, `scale_all.sh`, `scale_table.py`; `runs/hero1/scale.jsonl`, `scale_summary.json` |
| run chain | `genome/hero1/eval_all.sh`, `extras.sh`, `extras2.sh`, `chain3.sh` |

Order of events: kernel verified; test set 1 written and hashed; this document's section 1; training data; training (one run) with the scale runs during it; evaluation; then (after seeing the test-1
results) the external test set 2 was ordered and its hash and protocol written into section 1b before it was run; then the extras. Paid API spend: $0.
