# HERO-6: the tiny seating model learns rules about NAMED guests (2026-09-30)

Swing 33. Order of writing: section 1 (kill rule, test sets, judge, intended page programs) was written and hashed after the
training data was generated and while the model was training, and BEFORE any output of the new model was generated. Everything after
section 1 was filled in after the runs.

## 1. Kill rule and protocol (frozen before any model output)

**Question.** Can the tuned Qwen3-1.7B read rules that name guests or companies ("keep Musk away from OpenAI", "seat Sacks with
Chamath") into two new stage words, `avoid X Y` and `pair X Y`, so the public page no longer needs hand-written lines, without
losing what it could already read?

**New independent test set (frozen).** `data/hero/policies_test6.json`, sha256
`72d1c42131946592727c58d2b15e9b6be4a95bd957c03ec5df41facca357fb1c`. 72 requests written by a separate subagent that saw only the
34 guest tokens, the plain meaning of the eight words, and the naming convention (it did not see the training generator, the training
data or the page sentences; it opened only `genome/hero6/lang6.py` to check its gold programs parse). Every request names at least one
guest or company; 30 also use old category words; 12 name INVENTED guests (16 invented guests listed in the file, 8 invented
companies). I checked only that all 72 gold programs parse; nothing was edited. Known overlap (checked after it was delivered, by
exact string search of the invented names in my already generated training texts): 1 of 16 invented person names (`Oluwaseun Adeyemi`) and
4 of 8 invented company names (Halcyon Capital, Kestrel Semiconductor, Lumen Robotics, Tidewater Partners) occur verbatim in the
training texts; both sides drew from common name stock. 0 of 72 test texts occur in training.

**Judge (frozen).** `genome/hero6/judge6.py`, sha256 `2bd2264580ca3b89db679af18ef625a0c5e24118740d34af742370efadd3fcc7`.
A sample PASSES iff it parses under the strict `lang6` parser and, on each of three guest lists - the real 34-guest chart, `synA`
(80 guests) and `synB` (101 guests) - the section assignment computed by the tag-mask sectioner net (HVM2 executor) for the sample's program
equals the Python reference assignment of the gold program. synA/synB = the 34 real guests + the 16 invented guests + invented
colleagues at real companies (10 and 11; so `OpenAI` and `Greg_Brockman` are different rules) + synthetic filler guests, shuffled with seeds 601/602.

**Pre-registered weakness of this criterion, and a stricter secondary.** Checked on gold programs only, before any model output: the
3-list criterion is lenient for named rules. An `avoid` line that is dropped goes unnoticed whenever the two guests land in different sections anyway:
8 of the 72 gold programs give the same seating as the EMPTY program on all three lists, and only 111 of 157 single-line deletions from
gold programs are detected. So I also report STRICT = pass AND the same seating as the gold on 100 probe lists (all 71 named
guests, no filler, 100 fixed shuffles); it detects 149/157 single-line deletions. Exact canonical program text is reported too.

**Regression sets (frozen by HERO-1).** `data/hero/policies_test.json` (set 1, sha256 `a758fb81...a480`) and
`data/hero/policies_test2.json` (set 2, sha256 `19c2df3d...c5ca9`), judged by the unchanged HERO-1 judge (`genome/hero1/pipeline.judge`,
HERO-1 parser: any `avoid`/`pair` line in an answer to these old policies is a parse error = fail). HERO-1 numbers: set 1 98.6% (355/360)
pass@1 at T = 0.7, n = 5, greedy 72/72; set 2 90.6% (326/360), greedy 65/72.

**Sampling.** Same prompt as HERO-1 (`genome/hero1/sample.py`), n = 5 samples at T = 0.7, top_p 0.95, seed 0, and greedy. pass@1 of a
policy = passed/5; headline = mean over policies.

**KILL RULE.** PASS iff (a) new independent set pass@1 (3-list criterion, T = 0.7, n = 5) >= 85% AND (b) set 1 pass@1 >= 95.6% and set 2
pass@1 >= 87.6% (no worse than 3 points). Otherwise PARTIAL (report which clause failed). If STRICT is below 85% while the 3-list
criterion passes, I will say that plainly next to the verdict.

**Page sentences (intended programs written first).** `runs/hero6/page_intended.json`, sha256
`d8a45e1ea1eb6a1d97775f953e9be7a27c01e17aeb9eff00212c647533abcce6`, 13 sentences (a-f, the five HERO-1 showcase sentences, and the two
old page sentences) with the intended program for each, written before the model was run.

**What is verified.** The tag-mask sectioner net (`genome/hero6/sectioner6.py`), one net, checked by `genome.verify` (hidden suite v2:
edge + random at authoring sizes and 16x + exhaustive small sweep) seeds 0-2, plus 5,000 extra random kernel inputs and 1,000 random
policies with `avoid`/`pair` end to end, against the Python reference. `pair` is host-side prep (like `together`), not in the net.

## Summary (plain language)

**Verdict: PARTIAL. Clause (a) passes, clause (b) fails on test set 1.**

- **New independent set (72 named-guest requests).** The tuned 1.7B gets **89.2%** pass@1: 321/360 samples at T = 0.7, n = 5, 95% CI [81.7, 95.6]. Greedy decoding gets 64/72 (88.9%). Bar: 85%.
  STRICT gets **85.0%** (306/360), just at the bar. Exact program text gets 85.0%. On the 12 requests with invented guests: 54/60 (90.0%).
- **Regression on test set 1.** **93.1%** (335/360), against 98.6% for HERO-1, a drop of 5.5 points. The kill rule allowed at most 3, so **this clause FAILS**. Greedy gets 67/72 (HERO-1: 72/72).
- **Regression on test set 2.** **88.1%** (317/360), against 90.6%, a drop of 2.5 points, so this clause passes. Greedy gets 63/72 (HERO-1: 65/72).
- **`avoid` is now part of the checked blocks.** Guests carry a tag bitmask (7 category bits plus up to 17 name bits), and every rule tests `(mask & tags) != 0`.
  - The new net passes `genome.verify` on seeds 0, 1 and 2 (103/103 hidden cases each).
  - It also matches the reference on 5,000/5,000 extra random kernel inputs.
  - End to end, it equals the JS-semantics reference on 1,000/1,000 random policies with avoid/pair. 777 of those use avoid, 597 use pair, and 250 run on the real chart.
  - `pair` is host-side prep, like `together`, so it is not in the net.
- **The page JS (`demo/luncheon/seating.js`) now has `pair`.** The Python reference matches it on 1,000/1,000 random cases (`node demo/luncheon/test_seating.js`):
  - all 400 old cases;
  - 600 new cases with avoid/pair (assignment, seat order, canonical text and every violation count);
  - the five showcase arrangements;
  - 393/393 brute-force avoid counts.
- **Page sentences (greedy).** 10 of 13 match the intended program. All six named sentences except (f) are right, and each gives 1 distinct program in 20 samples at T = 0.7. Sentence (f) drops "colleagues together". Two old showcase sentences are misread: show4 (as in HERO-1) and **show5, which HERO-1 read correctly**: "Pairs only, please" now loses `size 2`.

The regression has one cause: the new words collide with old wording. Clipped size clauses and the word "pairs" fail on test set 1:
- "Pairs only." -> `pair chips software`;
- "Cap 3." dropped;
- "Sections of 3. Chip makers together." -> `limit chips 3`;
- "chips and software apart" -> truncated token `software`.

## 2. What was built

| piece | file | check |
|---|---|---|
| language: six HERO-1 words unchanged (imported) + `avoid X Y`, `pair X Y`; reference prep/sectioning/checker; tag-mask net input | `genome/hero6/lang6.py` | `genome/hero6/selftest6.py`: old words identical to HERO-1 on 3,000/3,000 random (assignment, order, canonical text, violations); canonical round-trip 3,000/3,000; tag-mask function == reference 3,000/3,000; an avoid pair shares a section only when one unit holds both sides (0 exceptions in 2,216) |
| page JS: `pair` added; `prep` uses each guest's own category (identical without pair); named lines canonical (sorted, symmetric) | `demo/luncheon/seating.js` | `node demo/luncheon/test_seating.js`: 1,000/1,000 cases match the Python reference (600 with avoid/pair), showcase all match, avoid brute force 393/393; old vs new seating.js identical on 3,000 random avoid programs on the real chart |
| verified tag-mask sectioner net | `genome/hero6/sectioner6.py` | `genome.verify` seeds 0-2 pass 103/103 each (`runs/hero6/verify_kernel.log`); a mutant (admission test inverted) fails 27 cases; `genome/hero6/stress6.py`: 5,000/5,000 kernel, 1,000/1,000 policies (`runs/hero6/stress6.json`) |
| training data | `genome/hero6/gen_train6.py` | 11,000 train + 300 valid. 4,060 are HERO-1 sentences (same generator, same held-out signatures excluded). 6,940 name guests: 5,078 with avoid, 3,376 with pair, 3,786 of them mixed with old words. 29,870 name tokens: 14,760 real (full names, surnames, a few first names, titles, companies, "Tesla"/"SpaceX" -> Elon_Musk), and 7,282 distinct invented names/companies |
| model | `adapters/hero6_1p7b`, `genome/hero6/train6.sh`, `runs/hero6/train_1p7b.log` | Qwen3-1.7B-4bit + LoRA (all layers, rank 8 default), lr 5e-5, prompt masked, seed 0. Batch 16 x 900 iterations instead of 8 x 1,200, for speed on a shared GPU: 14,400 examples, about 1.3 epochs. Validation loss 0.011 at iteration 450, 0.001 at 900. About 45 min |
| judge / eval | `genome/hero6/judge6.py`, `eval6.sh`, `report6.py`, `page6.py` | samples in `runs/hero6/samples/`, scores `*.scored.json`, `runs/hero6/report.json` |

Semantics of the new words (module doc of `lang6.py`, identical to `seating.js`):
- **Matching.** A guest matches X iff key(name) == X or key(org) == X. key() writes every run of spaces or commas as `_`.
- **`avoid`.** Next-fit with one (hasX, hasY) flag pair per word. A unit's first element is blocked if any member of the unit matches one side while the section already has the other. Later elements are checked by themselves. The flags reset on a new section.
- **`pair`.** Union-find over units: every unit holding a guest who matches X or Y is merged. The merged unit sits at its earliest part's position, its members in part order, and each guest keeps its own category.
- **Checker.** avoid counts (x, y) pairs with x != y in the same section; pair counts them in different sections.

**What is and is not in the checked blocks.**
- Checked by `genome.verify` and the stress runs: sectioning with size, limit, apart and avoid. These are all rules of one form, (mask, mask, k), over tag bitmasks, including the unit look-ahead.
- Host Python/JS, not a net, as in HERO-1: unit building (`together`, `pair`), the priority sort (`order`), and name matching (which guest gets which tag bit).
- Limit: at most 17 distinct names across the avoid words of one program. Above that, `tag_input` refuses.

## 3. Results

### 3.1 New independent set (`data/hero/policies_test6.json`, 72 requests)

| T=0.7, n=5 | policies | passed / samples | pass@1 [95% CI] | exact text | parsed |
|---|---|---|---|---|---|
| all (kill-rule criterion: real 34 + synA + synB) | 72 | 321/360 | **89.2%** [81.7, 95.6] | 85.0% | 98.1% |
| all, STRICT (+ 100 probe lists) | 72 | 306/360 | 85.0% | | |
| invented guests | 12 | 54/60 | 90.0% [71.7, 100] | 90.0% | 93.3% |
| real guests only | 60 | 267/300 | 89.0% [80.7, 96.3] | 84.0% | 99.0% |
| avoid only | 32 | 146/160 | 91.2% [81.2, 99.4] | 85.0% | |
| pair only | 27 | 115/135 | 85.2% [70.4, 96.3] | 85.2% | |
| avoid and pair | 13 | 60/65 | 92.3% [76.9, 100] | 84.6% | |
| named words only | 42 | 196/210 | 93.3% [85.2, 99.5] | 88.6% | |
| named + old category words | 30 | 125/150 | 83.3% [70.0, 96.7] | 80.0% | |
| greedy, all | 72 | 64/72 | 88.9% [80.6, 95.8] | 84.7% | 97.2% |
| greedy, STRICT | 72 | 61/72 | 84.7% | | |

Failures: 9 policies, 8 of them 0/5 (`runs/hero6/samples/test6_t07.scored.json`).
- **avoid read as pair**, when the sentence does not use a usual "away from" phrasing:
  - n16 "keep Sacks, Gerstner and Palihapitiya from sharing a section with Musk" -> pair lines;
  - n58 "Separate: Musk/Nadella, Bezos/Pichai, Zuckerberg/Huang" -> the last two as pair;
  - n47, a trailing "Musk ... away from Bezos" clause -> pair.
- **Surnames never seen in training:**
  - "Daniels" -> `Bill_Daniels` (n17);
  - "Su", "Tan" -> `Su` or `Arjun_Tan` (n20, n68).

  Training used "Rahbar Daniels", "Dr. Su" and "Hock Tan" only. For unknown surnames the model invents a name, and since that name matches no guest the rule silently does nothing.
- **Old-word failures:**
  - "security first" -> `order security`, a parse error (n47, n72);
  - "Together company" (capitalised, at the start of the sentence) dropped (n60).
- **One typo in an invented name:** `Arjun_Mehhta` (n29, 1 of 5).

### 3.2 Regression (unchanged HERO-1 judge)

| set | HERO-1 adapter | HERO-6 adapter | change | clause |
|---|---|---|---|---|
| set 1, T=0.7 n=5 | 355/360 = 98.6% | 335/360 = **93.1%** [87.5, 98.6] | -5.5 | **FAIL** (allowed -3) |
| set 1, greedy | 72/72 | 67/72 | -5 policies | |
| set 2, T=0.7 n=5 | 326/360 = 90.6% | 317/360 = **88.1%** [80.6, 95.0] | -2.5 | pass |
| set 2, greedy | 65/72 | 63/72 | -2 policies | |

Set 1 failures (5 policies, all 0/5):
- `ter05` "Pairs only. Chips and software apart." -> `pair chips software`. The new word `pair` captured "Pairs", and "software" was truncated.
- `ter08` "Cap 3. Government officials first." -> `size 3` dropped.
- `ter12` "Sections of 3. Chip makers together. ..." -> `limit chips 3` instead of `size 3` + `together chips`.
- `lis04` "chips and software apart" -> `apart chips software`, which does not parse.
- `cha12`, the same dropped "Sections of three" as HERO-1.

All five are terse/list voices with clipped size clauses or a bare "software". On set 2 the misses are the HERO-1 ones (a29, a38, a49, a56, a57, a63, a72) plus a21 (2/5) and a35 ("fund person" -> `apart investor`, a parse error).

### 3.3 Page sentences (`runs/hero6/page_outputs.json`; greedy, then 20 samples at T = 0.7)

| id | sentence (short) | greedy program (canonical) | = intended | distinct programs in 20 @T0.7 | intended in 20 | secs | tokens in/out |
|---|---|---|---|---|---|---|---|
| a | gov 1 + Musk away from OpenAI, Zuckerberg | `limit government 1; avoid Elon_Musk Mark_Zuckerberg; avoid Elon_Musk OpenAI` | yes | 1 | 20 | 0.41 | 71/20 |
| b | Musk away from Bezos, Zuckerberg, OpenAI | `avoid Elon_Musk Jeff_Bezos; avoid Elon_Musk Mark_Zuckerberg; avoid Elon_Musk OpenAI` | yes | 1 | 20 | 0.48 | 65/24 |
| c | Sacks with Chamath | `pair Chamath_Palihapitiya David_Sacks` | yes | 1 | 20 | 0.31 | 67/12 |
| d | Brockman, Amodei, Brown together | `pair Dario_Amodei Greg_Brockman; pair Greg_Brockman Tom_Brown` | yes | 1 | 20 | 0.43 | 68/19 |
| e | Microsoft+OpenAI together, Google away | `avoid Google Microsoft; avoid Google OpenAI; pair Microsoft OpenAI` | yes | 1 | 20 | 0.34 | 64/13 |
| f | sections of 4, colleagues together, Musk not near Zuckerberg | `size 4; avoid Elon_Musk Mark_Zuckerberg` | **no** (dropped `together company`) | 1 | 0 | 0.32 | 65/12 |
| show1 | | `size 4; together company; limit government 1` | yes | 1 | 20 | 0.32 | 71/12 |
| show2 | | `size 5; apart ai_lab big_tech; order chips` | yes | 1 | 20 | 0.34 | 73/14 |
| show3 | | `size 3; together investor; apart ai_lab chips` | yes | 1 | 20 | 0.32 | 73/13 |
| show4 | | `limit software_security investor 2; limit software_security government 2` | **no** (HERO-1 also misread it) | 2 | 0 | 0.33 | 71/13 |
| show5 | "Pairs only, please. ..." | `limit big_tech investor 1; limit big_tech investor 1; order big_tech ai_lab` | **no** (HERO-1 read it correctly) | 7 | 0 | 0.46 | 69/22 |
| gov1 | No two government officials in one section. | `limit government 1` | yes | 1 | 20 | 0.20 | 58/4 |
| easy | AI labs and big tech apart. Sections of 5. | `size 5; apart ai_lab big_tech` | yes | 1 | 20 | 0.31 | 62/11 |

Seconds are single greedy requests on a shared machine, with one warm-up excluded.

## 4. Caveats

1. **The 3-list criterion is lenient for named rules** (pre-registered in section 1): 8 of 72 gold programs equal the empty program on those lists. STRICT (85.0%) is the more honest number, and it sits exactly on the bar.
2. **Recipe change.** Batch 16 x 900 instead of 8 x 1,200, chosen for speed before any result. Not ablated: the regression could partly come from the recipe rather than the data mix. One run, one seed.
3. **Surname coverage is memorised, not general.** The model maps only the surnames it saw in training. Unknown surnames become invented tokens that match nobody, and the rule then silently does nothing. The page should show the program and flag names that match no guest.
4. **Invented-name overlap.** 1/16 invented person names and 4/8 invented company names of the test set occur verbatim in training, by coincidence (common name stock). The 12 invented-guest requests are too few to separate this effect.
5. **Same author for the words, the generator and the intended page programs.** The 72-request test set came from a separate subagent. Test n-gram share found in training: 93% of words, 72% of bigrams, 38% of trigrams, 18% of 4-grams, 8% of 5-grams (`runs/hero6/overlap6.json`).
6. **`pair` is not in the net.** It is unit building on the host, the same status as `together` and `order` in HERO-1. Name matching to tag bits is also host code.
7. **The page is being edited concurrently by another agent.** `demo/luncheon/index.html` was rebuilt at 19:52 and already includes the new `seating.js`. I did not edit `app.js` or `template.html`.

## 5. Files

`genome/hero6/{lang6,selftest6,sectioner6,stress6,gen_train6,judge6,report6,page6}.py`, `genome/hero6/{train6,eval6}.sh`;
`runs/hero6/{train_1p7b.log,train_meta.json,valid_set.json,verify_kernel.log,stress6.json,overlap6.json,page_intended.json,page_outputs.json,report.json,eval6.log}`,
`runs/hero6/samples/*`, `runs/hero6/seating.js.before`; `adapters/hero6_1p7b/`; `data/hero/policies_test6.json`;
`demo/luncheon/{seating.js,gen_cases.py,test_seating.js,cases.json}`. Paid API spend: $0.
