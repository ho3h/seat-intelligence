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
