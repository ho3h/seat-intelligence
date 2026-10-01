# HERO-4: a vocabulary that grows after the small model is trained (swing 31, 2026-09-30)

Code: `genome/hero4/`. Runs, samples, logs: `runs/hero4/`. Ground rules: docs/HERO-SEATING.md (local compute only, no paid API, company / category
fields only, nothing personal). Independent of HERO-1 (its files were not used; it shared the GPU, and my training queued behind it).

## 0. Kill rule and verdict

**Kill rule (written before any model run).** New words must reach **>= 70% pass@1** on their own family through a **prompt-only** addition (signature,
gloss and one worked example added to the prompt's word block; no retraining, no weight change) on **>= 6 of the 10** new families, with **base-family
regression <= 5 points** when the new entries are in the prompt. 30 tasks x 4 samples = 120 samples per family and arm. The arm I pre-registered for
regression is "base tasks with all ten new entries in the block".

**Verdict: PARTIAL. The threshold clause is met at the minimum and replicates; the regression clause as pre-registered is NOT met. The strict verdict is that the kill rule is not cleanly passed.**

| clause | result |
|---|---|
| >= 70% on >= 6 of 10 families, prompt-only (arm B: base block + that family's entry), test v1 (the pre-registered set) | **6 of 10** (exactly the minimum): pair 91.7, apart 79.2, vip 100.0, stagger 88.3, headseat 95.0, bigfirst 80.0. Four more fail: waitlist 57.5, snake 25.8, limit 10.0, sectionlead 0.0. Only 4 of the 6 have a 95% CI lower bound >= 70 (pair, vip, stagger, headseat) |
| replication on a fresh test set (test v2: new wording writers, new parameters, same round-1 entries) | **6 of 10** again: pair 98.3, apart 84.2, vip 97.5, stagger 98.3, headseat 100.0, bigfirst 86.7; waitlist 69.2 (just under), snake 24.2, limit 15.0, sectionlead 3.3 |
| base regression, pre-registered arm (all ten entries in the block) | **fails**: -9.2 points [-13.8, -4.7] on test v1 (98.3 -> 89.2 pooled, 590/600 -> 535/600), -8.0 [-12.8, -3.8] on test v2 |
| base regression, one new word added at a time (post-hoc arm, added after I saw the all-ten result) | **passes**: 0.0 points [-0.7, +0.8] on test v2 (574/600 both) |

So: adding ONE word after training works for six of ten words and costs the base families nothing. Adding all ten to one prompt makes the tuned 1.7B
model start using look-alike new words in place of base words (`stagger 6` where `sections 6` is right, `vip` for `order rank`), and base accuracy drops
8-9 points. Four words fail outright, mostly for one reason (section 5).

Pooled over the ten families (test v1, 1,200 samples each): base-only block **3.2%** (39/1200, all of it tasks where the new word is a no-op, section 4),
**+ own word 62.8%** (753/1200; +59.5 points paired [+53.7, +65.4]), + all ten 59.2% (711/1200).

Controls (test v1, 1,200 samples each): **untuned Qwen3-4B-Instruct with all 15 entries in the prompt: 31.6% pooled, 1 of 10 families >= 70** (base families 38.7%: 519 of its 1,800 samples do not even parse, for example a stray second closing word). The tuned 1.7B with the prompt-only word beats it by 31 points.
**Retraining the 1.7B with the ten words in its data** (about 250 extra phrasing sentences from a third writer; 42 minutes of training on an idle GPU, about 2 hours on the shared one): **98.2% pooled, 10 of 10 families >= 91.7, base 99.3%**. So retraining dominates the prompt-only route in accuracy, including on the four words that prompt-only cannot do;
prompt-only buys "no training run" at a cost of about 35 points of pooled accuracy and, for the full library, 8-9 points of base accuracy. Without alias training (ablation G) only 2 of 10 words work (37.4% pooled).

Cost to author a word (section 6): **mean 28 s of tool-clock, 1.0 verifier attempts (10 of 10 first-try passes), 3.8 net lines, about 170 tokens of artefacts (reference + net + block entry)**.
It does **not** fall from word 1 to word 10 (limit 35 s / 182 tokens, sectionlead 37 s / 214 tokens). Everything that could be cheap was already
built (223 lines of net fragments, written first and not charged to any word). The expensive part is not authoring the net: it is the entry that the small model must read,
and three rounds of dev-set revision (about 30 minutes of wall clock, mostly sampling and scoring on a shared machine) did not make limit, snake or sectionlead work.

## 1. Design (frozen before any model run; deviations are listed in section 8)

(Section 1 was written at about 09:50, before any model run, and the kill rule above has not been changed. This final version compresses it and moves everything that came later to section 8.)

### 1.1 Domain: what a word is
Guest = one u24 number: `idx` (6 bits) | `rank` (5 bits, the game's numeric RSVP-order field, a host-side number) | `category` (3 bits, from
`data/hero/luncheon.json`) | `company` (5 bits, 19 printed companies, 0 = none). A seating program is a list of ARRANGE words (list -> list, a permutation)
followed by exactly ONE CLOSING word: `sections S` (output every guest's section, the table cut into runs of S seats) or `captains S` (only each
section's captain). Text order = program order. An arrange word is defined by a Python reference (`genome/hero4/refs.py`); its net
(`words.py`, `newwords.py`) must equal the reference on the hidden suite (`genome.verify`: edge + random + big + exhaustive small, suite v2).
The words are best-effort ARRANGEMENT HEURISTICS defined exactly by their reference (for example `limit` deals a block of k guests of the category and
S-k others in turn; if the counts make the rule infeasible it degrades deterministically). They are not constraint solvers.

Every net is `annotate -> stable insertion sort -> strip` (closing words are one scan). The fragments (expression compiler, counter bank,
position-threaded scan, first pass of a two-pass word, sort, strip: `netlib.py`) are infrastructure written once, with the five base words.

### 1.2 Vocabulary
BASE (5; the small model is tuned on these only): `group company|category`, `spread`, `order rank|rank desc|category <c>..|company <Co>..`,
`sections S` (closing), `captains S` (closing).
NEW (10; authored one at a time in this fixed order): 1 `limit <cat> <k> <S>` (at most k of a category per section) 2 `pair <A> <B>`
(A next to B) 3 `apart <CoX> <CoY>` (two companies at opposite ends) 4 `vip <R>` (rank <= R first) 5 `stagger <m>` (rounds, at most m per company per
round) 6 `headseat` (lowest rank takes seat 1) 7 `bigfirst` (larger company delegations first) 8 `waitlist <cat> <k>` (only the first k of a category
keep their place, the rest go last) 9 `snake <S>` (every second section reversed) 10 `sectionlead <S>` (lowest rank takes the head seat of each section).
The word block entry of each (signature, gloss, one worked example) is in `genome/hero4/lang.py` (`ENTRIES`). It is exactly what a frontier author adds.

### 1.3 Model and prompt
Qwen3-1.7B-4bit, LoRA rank 8 on all layers, batch 8, 600 iterations, lr 5e-5, prompt masked (exp15 recipe), 6,000 training prompts, val loss 0.000.
Prompt = header + WORD BLOCK + category and company token lists + the host's rules. **Alias training (a design decision made up front):** each base
word's shown name is drawn per example from a pool of five, so the block is the only place that says what a name means; this tunes "read the block"
without exposing any new word. Ablation G below removes it. Training text: single-sentence templates from two independent phrasing writers (40 per base kind each; the last 8 of each
writer's list held out of training and used for the iid check), joined in program order with random parameters. No test text appears in training.

### 1.4 Test sets (frozen before sampling; sha256 of the files)
Wording was written by independent subagent writers who saw only a plain description of the host's wish and its parameters, never the word names,
signatures, glosses, examples or any code. Tasks were split round-robin so that no writer owns a family. Each family is 30 tasks.
* **test v1** (pre-registered): 10 new families x 30 + 5 base families x 30. `runs/hero4/sets/FROZEN/test_final.json` sha256 `a4785a7d8bd62d1c745f6c8c70accb9045fe02062e00ae7ef036520c60c65a77`, frozen 09:50.
* base iid check (held-out training templates): `FROZEN/iid_base.json` `e41794e84b2b01a4b62c20ae7d43de29eaf1c377ba50022474e443acb5ef2d94`.
* **dev** (20 tasks per new family), **test v2** (30 per new family), **base dev** (20 per base family), **base test v2** (30 per base family), all fresh
  wording and parameters, written AFTER I saw round-1 results, used for the entry-revision round and the replication: `FROZEN2/dev_final.json` `d4f94ae8...8d07`,
  `testv2_final.json` `1b5e55a7...761a`, `bdev_final.json` `490aab27...796f`, `btv2_final.json` `87e5a46f...157f` (full hashes: `shasum -a 256 runs/hero4/sets/FROZEN2/*`).
* Gold coverage: all 347 distinct gold programs of test v1 and all 100 of the iid set assemble into one net that passes `genome.verify` (coverage 100%).

### 1.5 Scoring
A sample passes iff it parses (one word per line, strict arities and token lists, exactly one closing word, last), its program is not refuted by the gold program on
60+ probe inputs, and its assembled net (all word templates piped by `genome.compose`) passes `genome.verify` seed 0 against the gold reference. Sampling:
n=4, temperature 0.7, top_p 0.95, max 120 tokens. CIs are 95% task-bootstrap intervals.

### 1.6 Arms
A base-only block. B base + the family's own entry (primary). C base + all ten entries. D base regression (base tasks under A and C; plus the post-hoc one-word arm).
E untuned Qwen3-4B-Instruct-2507 with all 15 entries. F retrain the 1.7B with the ten words in its data. G ablation: base tuning without alias names.

## 2. Word verification
51 instances (14 base, 37 new; new words at 4-5 parameter settings each, including edge settings such as k >= S, S = 1, R = 0 and unused categories) each pass
`genome.verify` at seeds 0, 1 and 2: 153/153 seed-runs (`runs/hero4/word_verify.json`). The suite discriminates: 11 deliberately wrong templates (wrong k, wrong category,
swapped arguments, another word's net) all FAIL (mutation check, `runs/hero4/mutation_check.json`: 11 of 11 mutants rejected). Base-word nets cost about 17-37k interactions at 34-48 guests.

## 3. Results, test v1 (pre-registered; round-1 entries)

pass@1 in % (passing samples / samples), 30 tasks x 4 samples per family.

| family | A. base-only block | B. + own word | C. + all ten | G. ablation: constant names, + own | E. untuned 4B-Instruct, all 15 | F. retrained 1.7B, all 15 |
|---|---|---|---|---|---|---|
| limit | 6.7 (8/120) | 10.0 (12/120) | 9.2 (11/120) | 8.3 (10/120) | 6.7 (8/120) | 100.0 (120/120) |
| pair | 0.0 (0/120) | 91.7 (110/120) | 82.5 (99/120) | 45.0 (54/120) | 20.0 (24/120) | 97.5 (117/120) |
| apart | 3.3 (4/120) | 79.2 (95/120) | 85.0 (102/120) | 32.5 (39/120) | 35.8 (43/120) | 96.7 (116/120) |
| vip | 5.8 (7/120) | 100.0 (120/120) | 98.3 (118/120) | 54.2 (65/120) | 75.8 (91/120) | 98.3 (118/120) |
| stagger | 0.0 (0/120) | 88.3 (106/120) | 86.7 (104/120) | 76.7 (92/120) | 26.7 (32/120) | 97.5 (117/120) |
| headseat | 3.3 (4/120) | 95.0 (114/120) | 80.8 (97/120) | 81.7 (98/120) | 69.2 (83/120) | 100.0 (120/120) |
| bigfirst | 0.0 (0/120) | 80.0 (96/120) | 70.0 (84/120) | 12.5 (15/120) | 49.2 (59/120) | 91.7 (110/120) |
| waitlist | 0.0 (0/120) | 57.5 (69/120) | 50.8 (61/120) | 26.7 (32/120) | 15.0 (18/120) | 100.0 (120/120) |
| snake | 0.0 (0/120) | 25.8 (31/120) | 29.2 (35/120) | 32.5 (39/120) | 10.8 (13/120) | 100.0 (120/120) |
| sectionlead | 13.3 (16/120) | 0.0 (0/120) | 0.0 (0/120) | 4.2 (5/120) | 6.7 (8/120) | 100.0 (120/120) |
| **all ten pooled** | 3.2 (39/1200); families >= 70: 0 | 62.8 (753/1200); families >= 70: 6 | 59.2 (711/1200); families >= 70: 6 | 37.4 (449/1200); families >= 70: 2 | 31.6 (379/1200); families >= 70: 1 | 98.2 (1178/1200); families >= 70: 10 |

Arm B 95% CIs: limit [2.5, 20.0], pair [81.7, 100.0], apart [65.0, 91.7], vip [100.0, 100.0], stagger [76.7, 97.5], headseat [86.7, 100.0], bigfirst [65.8, 92.5], waitlist [40.0, 74.2], snake [11.7, 42.5], sectionlead [0.0, 0.0].

Reading it:
* **B vs A: +59.5 points paired [+53.7, +65.4] over 300 tasks.** Prompt-only addition does carry the new words.
* Six families pass the bar. The other four fail for identifiable reasons (section 5), not random noise: for `snake` and `sectionlead` the model uses the word and gets its line
  exactly right (90.8% and 96.7% of samples contain the exact gold line) but forgets the mandatory closing line.
* Arm C (all ten at once): pooled 59.2%, six families still >= 70 (bigfirst sits exactly at 70.0), but interference is visible (waitlist, pair, headseat, bigfirst drop).
* **Ablation G (no alias training): 37.4% pooled, 2 of 10 families >= 70** (stagger, headseat). The block-reading skill that alias training gives is what makes six of ten words adoptable.
* Control E (untuned Qwen3-4B-Instruct-2507, all 15 entries, zero-shot): pooled 31.6% (379/1200), 1 of 10 families >= 70; per family limit 6.7, pair 20.0, apart 35.8, vip 75.8, stagger 26.7, headseat 69.2, bigfirst 49.2, waitlist 15.0, snake 10.8, sectionlead 6.7. Its base-family pass@1 in the same run: 38.7% (232/600) over the 150 base tasks.
* Control F (retrain the 1.7B with the ten words in training data, then all 15 entries in the block): pooled 98.2% (1178/1200), 10 of 10 families >= 70; per family limit 100.0, pair 97.5, apart 96.7, vip 98.3, stagger 97.5, headseat 100.0, bigfirst 91.7, waitlist 100.0, snake 100.0, sectionlead 100.0. Its base-family pass@1 in the same run: 99.3% (596/600) over the 150 base tasks.

## 4. Base regression

| base set | block | group | spread | order | sections | captains | pooled (samples) | paired delta vs base-only, points [95% CI] |
|---|---|---|---|---|---|---|---|---|
| test v1, 150 base tasks (independent wording) | base-only | 98.3 | 100.0 | 93.3 | 100.0 | 100.0 | 98.3 (590/600) | - |
| test v1, 150 base tasks (independent wording) | + all ten (r1) | 93.3 | 86.7 | 80.8 | 95.8 | 89.2 | 89.2 (535/600) | -9.2 [-13.8, -4.7] |
| test v1, held-out training templates (iid) | base-only | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 (600/600) | - |
| test v1, held-out training templates (iid) | + all ten | 96.7 | 96.7 | 90.0 | 100.0 | 80.8 | 92.8 (557/600) | -7.2 [-10.8, -3.7] |
| test v2, 150 base tasks (fresh wording) | base-only | 93.3 | 96.7 | 88.3 | 100.0 | 100.0 | 95.7 (574/600) | - |
| test v2, 150 base tasks (fresh wording) | + one rotating word (r1) | 93.3 | 95.8 | 89.2 | 100.0 | 100.0 | 95.7 (574/600) | +0.0 [-0.7, +0.8] |
| test v2, 150 base tasks (fresh wording) | + one rotating word (r2) | 93.3 | 93.3 | 89.2 | 100.0 | 100.0 | 95.2 (571/600) | -0.5 [-1.5, +0.2] |
| test v2, 150 base tasks (fresh wording) | + all ten (r1) | 86.7 | 81.7 | 80.0 | 96.7 | 93.3 | 87.7 (526/600) | -8.0 [-12.8, -3.8] |
| test v2, 150 base tasks (fresh wording) | + all ten (r2) | 83.3 | 79.2 | 82.5 | 96.7 | 95.8 | 87.5 (525/600) | -8.2 [-12.3, -4.2] |

Notes: (1) the test-v1 base-only model is at 98.3% pooled on independent wording and 100.0% on held-out training templates, so regression is measured from a high, clean baseline.
(2) Errors in the all-ten arm are almost all substitutions: of the 65 failing base samples in arm C (test v1), 53 contain a new word: `vip` in 23 (written in place of `order rank`, e.g. `vip 4`), `stagger` in 20 (in place of `sections`, unparseable because
`stagger` takes one number and is not a closer), `bigfirst` in 11, `headseat` in 1. Only 12 failures have no new word. (3) The one-word arm is what "add a word when a rule is not covered" looks like; the all-ten arm is the library after ten additions.

## 5. Why four words fail, and what the entry rounds did

Failure census for arm B (test v1, 120 samples per family):
* `sectionlead` (0.0%) and `snake` (25.8%): the word takes the section size as its only number, so it looks like a closing word. The model writes `sectionlead 8` and stops: 116/120 and 81/120 of the samples are
  rejected as "no closing word". If the gold closing line is appended to such samples (a diagnostic, never the headline), the pass rates would be **snake 82.5%, sectionlead 86.7%**.
* `limit` (10.0%): the section size has to be written twice (`limit chips 2 7` ... `captains 7`). The model drops the third argument in 39 samples and the closing word in 56. With the closing repaired it is 48.3%.
* `waitlist` (57.5%): 40/120 samples do not use the word at all and write the look-alike base word (`order category government`); the model prefers a base word it was tuned on.
* `apart` (79.2%) loses 18/120 samples the same way (`order company X Y`).

**Entry revision round (round 2; dev set only, three attempts, `runs/hero4/entry_log.jsonl`).** On the fresh dev set the round-1 entries gave limit 2.5, snake 27.5, sectionlead 5.0 (same pattern). Attempt 1 marked the three as arrangement words and used two-line
examples (limit 42.5, snake 57.5, sectionlead 18.8 on dev). Attempt 2 made the warning stronger (32.5 / 53.8 / 7.5, no gain). Attempt 3 put a uniform "ARRANGEMENT word (not a closing word)" tag on all ten entries
(dev: limit 32.5, snake 60.0, sectionlead 18.8, waitlist 70.0, others within a few points; base dev regression with all ten -13.2 vs -16.8 before). I stopped at three attempts and froze attempt 3 (`runs/hero4/entries_v2_FROZEN.json`,
sha256 `319bb5e5...b2e2`). Evaluated on test v2: limit 33.3, snake 35.8, sectionlead 12.5 (all up from 15.0 / 24.2 / 3.3) but **apart fell 84.2 -> 64.2, vip 97.5 -> 90.8 in arm B, and 5 instead of 6 families pass**.
Base regression with the revised entries: -0.5 [-1.5, +0.2] one-word, -8.2 [-12.3, -4.2] all ten, i.e. unchanged.
Conclusion: for these words a better entry is not enough. The behaviour (every training program ended with one closing line carrying the one number in the text) sits in the weights.
The round-2 idea came from the test-v1 failure census, so it is informed by test v1, which is why I replicated on fresh sets rather than re-scoring test v1.

**Table B. Fresh test v2** (new wording writers, new parameters; r1 = round-1 entries, r2 = revised entries frozen after the dev round). pass@1 % (passing/samples), 30 tasks x 4 per family.

| family | base-only | own, r1 entries | all ten, r1 | own, r2 entries | all ten, r2 |
|---|---|---|---|---|---|
| limit | 3.3 (4/120) | 15.0 (18/120) | 15.8 (19/120) | 33.3 (40/120) | 34.2 (41/120) |
| pair | 0.0 (0/120) | 98.3 (118/120) | 74.2 (89/120) | 94.2 (113/120) | 80.0 (96/120) |
| apart | 0.0 (0/120) | 84.2 (101/120) | 92.5 (111/120) | 64.2 (77/120) | 93.3 (112/120) |
| vip | 6.7 (8/120) | 97.5 (117/120) | 92.5 (111/120) | 90.8 (109/120) | 88.3 (106/120) |
| stagger | 0.0 (0/120) | 98.3 (118/120) | 94.2 (113/120) | 93.3 (112/120) | 96.7 (116/120) |
| headseat | 0.0 (0/120) | 100.0 (120/120) | 90.8 (109/120) | 100.0 (120/120) | 87.5 (105/120) |
| bigfirst | 0.0 (0/120) | 86.7 (104/120) | 74.2 (89/120) | 88.3 (106/120) | 90.0 (108/120) |
| waitlist | 0.0 (0/120) | 69.2 (83/120) | 40.0 (48/120) | 68.3 (82/120) | 47.5 (57/120) |
| snake | 3.3 (4/120) | 24.2 (29/120) | 29.2 (35/120) | 35.8 (43/120) | 42.5 (51/120) |
| sectionlead | 13.3 (16/120) | 3.3 (4/120) | 4.2 (5/120) | 12.5 (15/120) | 13.3 (16/120) |
| **all ten pooled** | 2.7 (32/1200); families >= 70: 0 | 67.7 (812/1200); families >= 70: 6 | 60.8 (729/1200); families >= 70: 6 | 68.1 (817/1200); families >= 70: 5 | 67.3 (808/1200); families >= 70: 6 |

## 6. Cost of authoring

| # | word | verifier attempts (seeds 0-2) | tool-clock s, start to end | reference lines | net lines | entry chars | est. tokens (reference + net + entry) | new fragment |
|---|---|---|---|---|---|---|---|---|
| 1 | limit | 1 | 35 | 6 | 4 | 146 | 182 | - |
| 2 | pair | 1 | 42 | 4 | 4 | 179 | 190 | - |
| 3 | apart | 1 | 27 (batch of 3: 82 s) | 3 | 3 | 192 | 132 | - |
| 4 | vip | 1 | 27 (batch of 3: 82 s) | 1 | 2 | 157 | 75 | - |
| 5 | stagger | 1 | 27 (batch of 3: 82 s) | 2 | 3 | 198 | 135 | - |
| 6 | headseat | 1 | 15 | 4 | 9 | 147 | 278 | two-pass aggregate (first use) |
| 7 | bigfirst | 1 | 23 | 4 | 3 | 172 | 156 | two-pass (reused) |
| 8 | waitlist | 1 | 23 | 4 | 2 | 206 | 155 | - |
| 9 | snake | 1 | 28 | 5 | 4 | 148 | 148 | - |
| 10 | sectionlead | 1 | 37 | 4 | 4 | 176 | 214 | two-pass (reused) |
| | **mean** | **1.0** | **28.5** | 3.7 | 3.8 | 172 | 166 | |

What the numbers say, and do not say:
* Every new word passed the hidden suite at seeds 0-2 on its first verifier attempt. The authoring step was small (a reference of 1-6 lines, an expression of 2-9 lines, a 150-200 character entry).
* **Cost does not fall from word 1 to word 10.** Word 1 (limit) 35 s / 182 tokens; word 10 (sectionlead) 37 s / 214 tokens; mean of the first five 143 tokens, of the last five 190. The only cost spike is
  the first use of a new fragment (word 6, `headseat`, 278 tokens, the two-pass aggregate); its reuse by `bigfirst` (156) and `sectionlead` (214, plus a position term) is cheaper. Reuse is real but small because the
  floor was already low.
* The per-word numbers are small because the expensive thing was written first and is not charged to any word: `netlib.py` (223 lines, 9.4 kB) and the five base words (75 lines, 3.4 kB), written in roughly eight minutes of tool-clock,
  with one wiring bug found by the verifier (a wire name mismatch in `captains`). `fold_bank_net`, the fragment `headseat` needs, had been written in that phase and not yet run; it worked on first use.
* The "seconds" column is the wall clock between my logged start and end events; it includes verifier time (5-28 s per word) and excludes the design of the rule, which I did up front for all ten words in one pass. apart, vip and stagger were written in one batch call
  (their start events were lost to a shell quoting glitch), so they are reported as a batch: 82 s for three.
* The true marginal cost of the four weak words is the entry iteration: three dev rounds, about 30 minutes of wall clock, no convergence.
* Token counts are characters/4 of what I wrote, not measured model tokens.

## 7. Disguised copies, novelty, and what the test does not show

* **Wording is independent, the concepts are not.** The neutral descriptions given to the writers were mine; the glosses are mine. Lexical overlap between a test text and its family's gloss + example (share of content words) is 5-41% by family
  (limit 5.0, apart 6.3, sectionlead 4.8, waitlist 12.4, pair 26.0, headseat 29.2, snake 29.5, vip 32.7, bigfirst 38.3, stagger 40.6). It does not explain success: apart (6.3%) passes at 79%, limit (5.0%) fails, stagger (40.6%) passes. Within the six passing
  families the low-overlap half of the tasks passes at 84.2% (n=90) and the high-overlap half at 93.9% (n=90). Pooled task-level correlation is 0.41, but within families it ranges 0 to 0.39. The words are not being matched by string copy.
* **Several "new" words are variants of base mechanics.** `vip` is a threshold version of `order rank`; `stagger` is `spread` keyed by company in waves; `bigfirst` is `group company` ordered by delegation size; `headseat` is a global-minimum version of `vip`; `waitlist` is a one-sided `limit`.
  The nets differ and each needs its own verified template, but the rules are not far from the base vocabulary. The four hardest words (limit, snake, sectionlead, waitlist) are not the most novel; they are the ones with a section-size argument or a base look-alike.
* **Vacuous tasks.** 23 of the 300 test-v1 new-family tasks are no-ops (the gold program is semantically equal to the same program without the new word, for example `snake S` or `sectionlead S` before `captains S`, which cannot change who captains a section). They are the only reason the base-only arm scores above zero (all 39 passing samples in arm A are on these tasks) and the reason `sectionlead` has 13.3% in arm A. The headline keeps them (pre-registered). Arm B with the word required and vacuous tasks dropped: limit 7.1, pair 96.4, apart 81.0, vip 100.0, stagger 88.3, headseat 100.0, bigfirst 80.0,
  waitlist 56.0, snake 16.3, sectionlead 0.0; the six-family conclusion is unchanged.
* **The task is translation.** The word is exact; the model only picks words and arguments. A regex parser could do this for template text, which is why the wording is independent. The hero claim (a 34-guest chart seated from one sentence) is not tested here.
* **Tuning a prompt entry on the same kind of tasks is part of the loop, and round 2 shows it is not free.** Round 1 entries were written before any sampling. Everything after the test-v1 census is informed by it.

## 8. Deviations from the plan, stated plainly
1. Added after seeing test v1: the vacuous-task analysis and the word-required metric; the closer-repair diagnostic; the one-word base-regression arm; dev / test v2 / base dev / base test v2 and the entry revision round. None of them changes the pre-registered numbers in section 0.
2. The `all` arm sampling crashed once with a Metal out-of-memory error at batch 48 (shared GPU); it was rerun at batch 16. Sampling is otherwise identical.
3. Training queued behind HERO-1's GPU job; the retrain control (F) and 4B zero-shot (E) ran late because the GPU was shared.
4. Controls E and F use test v1 with round-1 entries. G uses the same.
5. The "seconds" of three words is a batch number (section 6).
6. Authoring tokens are estimates.

## 9. Files
`genome/hero4/`: `refs.py` (semantics), `netlib.py` (fragments), `words.py` (base words), `newwords.py` (the ten new words), `lang.py` (language, block entries, prompts), `tasks.py`, `data.py`, `sample.py`, `score.py`, `report.py`, `tables.py`, `author.py`, `verify_all.py`, `train.sh`.
`runs/hero4/`: `authoring_log.jsonl`, `entry_log.jsonl`, `word_verify.json`, `sets/` (frozen sets and writer inputs/outputs), `samples/*.json` and `*.scored.json`, `entries_v2_*.json`, train logs, `summary.json`.
