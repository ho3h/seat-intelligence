# Review pack: everything, before anything goes public (2026-09-30)

Nothing has been published. The repo has an empty git history. The demo page is a local file.

## 1. The honest one-paragraph version
Machine authors can write correct programs directly as interaction nets, and the executor can check them exactly. That is real and mostly new as an end-to-end loop. It is NOT faster than a fair human-language route: with equal author effort, Bend ties native on graph and reconciliation programs (87 programs: depth Bend/native 0.55x geomean, native shallower on 39, Bend on 48; native about 22% less work at the median; a strong-Bend reconciliation at 100k is within 1.34x of native). The defensible claims are about authoring, verification and composition, plus a few medium-specific wins (the machine-applied K-cell lookahead; a verified auto-parallelizer that needs tree-shaped input; equivalence proofs for plumbing). Gate 1 was not passed as pre-registered (88% native against a 90% bar, seed 0 only).

## 2. Where to look, in order
| What | Where |
|---|---|
| The demo | `demo/luncheon/index.html` (serve: `python3 -m http.server 8765 --directory demo/luncheon`; preview name "luncheon") |
| Plain-language findings, with retractions | `docs/WHAT-WE-LEARNED.md` |
| Scoreboard, all 32 swings and their kill rules | `docs/SWINGS.md` |
| Gate status and dated bullets | `gates/STATUS.md` |
| The hero problem and ground rules | `docs/HERO-SEATING.md` |
| The five last-ditch tests | `docs/HERO-1.md` ... `docs/HERO-5.md` |
| Methodology mistakes found and fixed | `docs/METHODOLOGY-REVIEW.md` |
| Fair Bend baseline and the author-effect correction | `docs/BEND-FAIR-BASELINE.md`, `runs/exp17/` |
| Use case, real-data workload | `docs/USE-CASE.md`, `docs/RECONCILIATION-SPEC.md`, `docs/RECON-*.md`, `docs/OPENSANCTIONS-NOTES.md` |
| Physics and primers given to authors (frozen) | `PHYSICS.md`, `BEND_PRIMER.md` |

## 3. Results at a glance (from the docs; see Section 5 for how each was checked)
Positive, checked:
- Frozen models write correct nets: G0 20/20 (Opus); G1 seed 0 native 176/200, Bend 189/200.
- Strong-author graph/reconciliation nets exist for all T3/T5 programs: T3 coverage closed (exp19, 12/12 fresh-seed pass), T5 order-dependent kernels closed (exp18, 21/21).
- Machine-applied K-cell lookahead: 51/76 nets transformed, 232/232 pass seeds 0-2, median depth -43.5%.
- Library composition and recipes lift weak authors: typed glue Haiku 2/10 to 6/10; recipes Haiku 1/16 to 10/16 (p = 0.006).
- HERO-1: a 1.7B model turns an English seating rule into a verified program: 98.6% on the designer's 72 rules, 90.6% on an independent set; an untuned local chatbot breaks a rule in 88% of answers, the pipeline in 0%.
- HERO-2: normalization proves 91/92 known-equal pairs, 0 false proofs on 46 unequal ones (scope: plumbing and inlining).
- HERO-3: verified auto-parallelizer, depth exponent 0.11 vs 1.0 on tree input (needs a caller-supplied balanced tree).
- HERO-5: exact explanations by re-execution (100/100); the trace itself failed (0/100).

Negative or narrow (said plainly):
- No across-the-board speed advantage over a fair Bend route. G4 (faster than the human route at 100k) not met.
- Union-find is about 3,650x faster than the net on the reconciliation workload.
- Small-model whole-net fine-tunes: 14-31% vs Bend 47-88%. Stage-level factorization works but only on a vocabulary we designed, and unseen wording is weak (43-78%).
- Vocabulary growth by prompt alone: 6/10 new words, with crowding; retraining fixes it (10/10).
- Superposition search: no advantage; plain enumeration with observational-equivalence merging wins (known technique).

## 4. Claims that must NOT be made (retracted or unsupported)
- "Native beats Bend by 3-107x" or "88% / median 34% win on graphs": author effect, retracted.
- "The optimizer is exact": inlining is not always exact under unlabelled DUPs.
- "Constrained decoding / repair / factorized wiring fixes the failure": all killed.
- "Superposition gives a synthesis speedup": no, and the merge-by-value idea is prior art.
- "A language grows by pasting words into a prompt": partial (6/10), crowding hurts.
- "Seats 100,000 guests in parallel": depth is linear (next-fit is sequential); it is exactness and cost, not parallelism.
- Anything implying the guests in the demo hold the rules, feuds or seating shown. The rules are the host's rules in a game.

## 5. What was checked by whom
Lead-audited or independently re-run: G0; first 4 of the swing-8 nets at 64x; 8 of the swing-18 nets on fresh seeds; fair-Bend comparison recomputed from the result files; exp19 (12/12 on fresh seeds 3 and 4, `runs/exp19/lead_audit_seeds34.json`); the demo page's seating function against the Python reference (400/400 random cases plus the five recorded arrangements).
Agent-reported only (numbers were read from their reports and result files, not re-run by the lead): HERO-1 through HERO-5, swings 20-27 except as noted, the 87-program Bend swarm's own verification logs (group 2 re-verified 44/44 itself), swing 21 stage factorization.
Before going public I recommend one script that re-runs every headline number from a clean checkout, and a second-reader pass on Sections 3 and 4.

## 6. Release blockers and decisions for you
1. **Real people in the demo.** Names come from the officially posted chart (public figures, public document). The rules are labelled a game and avoid personal traits, but a seating game with named people can still read as a claim. Decide: keep names, use roles only, or publish with a short "not affiliated, not a claim" note. Also the chart image was provided by you from the posted document; we store a copy at `data/hero/luncheon_chart.jpg` (ignored by git). Do not redistribute the image without checking its terms.
2. **OpenSanctions data** is CC BY-NC 4.0 (research use only). `data/` is gitignored. `runs/exp16` and `runs/exp21` hold results derived from it (700 KB each); check whether they embed entity ids or names before including them. Do not ship the raw file or derived entity lists in a public repo without reading the license.
3. **Secrets.** `.env` and `.env.rtf` hold the OpenRouter key and are gitignored. A scan of the tree found no key strings outside them. Rotate that key before any public release anyway, since it was in a working directory shared with many agents.
4. **Size.** `adapters/` is 983 MB (LoRA weights), `runs/` 164 MB (`runs/hero4` 64 MB), `data/` 410 MB (excluded), `scratch/` 71 MB (excluded). Suggest: publish code, docs, nets and small results; put adapters on a model hub; exclude scratch and data.
5. **Upstream code.** HVM2 is Apache-2.0 and vendored under `physics/hvm2` (pinned); HVM4 and Bend are pinned clones. Prefer pinning by commit hash and a setup script over vendoring.
6. **Frozen artifacts.** `PHYSICS.md`, `BEND_PRIMER.md`, the corpus MANIFEST and `gates/g1/prereg.md` must stay byte-identical, since results depend on them.
7. **Stale process cleanup and repo hygiene.** Seven orphaned `hvm run` processes were killed. The git repo has no commits. There are `__pycache__`, `.pytest_cache`, `.DS_Store` files to drop.
8. **Naming.** Decide the public name and one-sentence pitch. The honest one: "Write a rule in English; a tiny local model turns it into a program you can check, run, and explain."

## 7. Still open
- G1 seeds 1 and 2 were never run, and Bend-X (renamed-keyword Bend) control is undone, so the Bend-familiarity confound is unmeasured.
- No strong-Bend comparison for the 7 exp18 and 6 exp19 nets.
- HERO-1 handles only the six stage words; out-of-scope requests silently become wrong programs 43% of the time (39/90); the parsed program must be shown to the host.
- The page cannot run the model in the browser; free-text rules are not supported.
- **No external benchmark number yet.** The 200-program corpus and its hidden suites were written by us, so every pass rate is internal. Candidate probes, in order: (1) the integer/list subset of MBPP+ / HumanEval+ (EvalPlus) through the G1 harness, native vs Bend with the same frozen authors; (2) the classic divide-and-conquer fold set from the parallelization-by-synthesis literature for HERO-3 (from memory, not yet looked up); (3) NATURAL PLAN calendar scheduling for HERO-1 (a scan, not a search, but needs the model to parse messy text). TravelPlanner is a poor fit: it needs a sound and complete solver (the 93.9% result uses GPT-4 plus Z3) and our seating kernels are greedy, not solvers. Proposed 2026-09-30, not run; downloads need approval.

