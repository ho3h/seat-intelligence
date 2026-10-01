# G1 pre-registration: does removing the human language pay?

Status: **drafted, not yet run.** Frozen when the runs start; thresholds below are the PRD's, with the ambiguities resolved in advance.
Blocked on: an author channel with an API key and a token cap (see "Cost").

## Fixed inputs
- Corpus: 200 programs, T1 30 / T2 30 / T3 50 / T4 40 / T5 50, frozen 2026-09-28, source hash `9a5d635c3fb20ea8` (`genome/corpus/MANIFEST.json`).
  No program is trimmed for any reason. A contract found to be wrong is fixed for both arms and every seed and the fix is logged.
- Physics: HVM2 v2.0.22 at `6542760`, unmodified. Depth from the instrumented copy `physics/hvm2-depth` (same rules, round scheduler).
- Native arm (primary): the author writes a net in HVM2's text IR. Primer `PHYSICS.md`.
- B1 (same author, human route): the author writes Bend 0.2.38; compiled with `-O all -O no-type-check`, primer `BEND_PRIMER.md`.
  Both primers carry one worked example on a non-corpus function. Same model, same attempt budget, same improvement rounds, same verifier suite.
- Author: a frozen Claude model (model id recorded per run), no tools, prompts built by `genome/contract.py`.
- Loop per (arm, program, seed): up to 5 submissions with feedback until a pass, then 2 improvement rounds (fewer interactions and depth), best passing kept.
- Verifier: suite v2 (edge + 24 random + 6 at 8x-16x + exhaustive small sweep), big cases folded by the type-directed digest, seed 0 to accept,
  fresh seeds 1 and 2 as audit. A program that fails either audit seed is void.
- Metrics per accepted program, at the largest test sizes, median over big cases: interactions and parallel depth. Wall-clock is reported (native arm64 C, this machine) and not gated.
- 3 authoring seeds = 3 independent sampled runs of the whole loop per arm.

## Pass criteria (PRD G1), evaluated on each of the 3 seeds
1. **Correctness:** at least 180 of 200 programs accepted (audit-clean) in the native arm.
2. **Beats the human route:** over programs accepted in both arms of the same seed, define the gain of a program as the larger of
   `1 - native_interactions/B1_interactions` and `1 - native_depth/B1_depth`. The native arm beats B1 on a program if its gain is positive.
   Native must beat B1 on at least 60% of those programs, and the median gain must be at least 25%.
3. All three seeds must satisfy 1 and 2. A seed that fails is a fail of G1, not an outlier to drop.

## Reported, never gating
Attempts per program, tokens and cost per accepted program, first-attempt rate, B3 anchoring arm (authors seeded with B1's compiled nets) and
structural distance between native nets and B1's compiled nets, the freedom diagnostic (share of coined words is 0 at G1), wall-clock.

## Outcomes (PRD stop rules)
Miss on correctness: one written revision to the author loop or the pen brought forward; never a smaller corpus.
Miss on power: continue to G2 anyway (a language may win where single programs do not).

## Cost and channel (needs a decision from Theo)
Measured at G0: an in-session subagent costs about 65,000 tokens of harness overhead per call for a 3,000-token prompt, so a full G1
by that route is roughly 100M tokens. Through the Messages API directly, one program is about 4 calls of about 7,000 tokens, so one
(arm, seed) is about 5M to 6M tokens and G1 (2 arms x 3 seeds) is about 30M to 40M. `genome/author_api.py` implements the loop with a hard
token cap (default 20M per invocation). Needs `ANTHROPIC_API_KEY` and a cap.

## Hashes of the frozen harness at drafting time
PHYSICS.md 2796c1d334de7f24
BEND_PRIMER.md 87a8933b9cae574b
genome/contract.py 8da789ed17ba13c4
genome/verify.py 13a043900a496d7e
genome/digest.py 6b15f7a7051e02f0
genome/bend_io.py f5444170956a2008
corpus MANIFEST sources 9a5d635c3fb20ea8


## Amendment 1 (2026-09-29, before any G1 run): author and loop, fixed after the Luna pilots
Decided on Theo's instruction to use GPT-6 Luna via OpenRouter (budget \$50). Pilots on the 20 G0 programs (instrument only, not G1 data):
- Luna, medium reasoning, no linter: native 15/20, B1 20/20 (\$0.26).
- Luna Pro, high reasoning, plus a static net linter (parse errors, wire-count errors, undefined refs; reads only the author's own net): native 19/20, B1 20/20 (\$1.21).
Frozen for G1: author = `openai/gpt-6-luna-pro`, reasoning effort high, same for both arms; native arm gets the linter as its counterpart of Bend's compiler errors.
The primary author is therefore not Claude (PRD default); this is a declared trade. Claude remains available as the second family for G2.
Linter false-positive check: 0 of 39 previously accepted nets flagged.
Run order: seed 0 for both arms on all 200 programs first, hard cap \$15 per arm; seeds 1 and 2 follow only if the remaining budget covers them.
Harness hashes at this point: PHYSICS.md f1af306e22b9f374, BEND_PRIMER.md 87a8933b9cae574b, verify.py b580b2c6d7e07057, contract.py 8da789ed17ba13c4, corpus sources 9a5d635c3fb20ea8.

## Result, seed 0 (recorded 2026-09-29; seeds 1 and 2 not run: budget)
Author: Luna Pro (high reasoning), then declared escalation of residual failures to DeepSeek V4 Pro (medium) in both arms (swarm, PRD system design).
Revisions used: (1) localised linter, primer pitfalls, free static rejects; (2) swarm escalation. This exceeds the PRD's single revision and is disclosed.
- Native: 176/200 audit-clean (88%); T1 30/30, T2 30/30, T3 35/50, T4 40/40, T5 41/50.  Bend: 189/200 (94.5%); T4 31/40.
- Both arms correct on 167 programs: native better on interactions or depth on 119 (71%), median gain 21%.
- Criterion 1 (>=180 native): MISS (176). Criterion 2 (>=60% wins and median >=25%): wins met, median gain missed. G1 is not passed on seed 0.
- Spend about $43.6 of $50. Findings: the author is the bottleneck on T3 and T5 hand-wired graph programs; T4 shows the opposite (native beats Bend).
