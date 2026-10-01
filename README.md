# Seat Intelligence

Write a seating rule in English. A tiny local model turns it into a few words of a program you can check, run, and explain.

This repo is the research record behind that demo. The research question was larger and mostly answered "no, not like that":
**can language models write programs directly as interaction nets (HVM2), skipping the human language (Bend), with the executor
acting as the verifier, and does that buy anything?** Models can write correct nets, and the executor checks them exactly. That
part is real. The hoped-for speed advantage over a fairly written human-language program mostly isn't (details below). What survived
is a smaller and more useful idea: a checked vocabulary of verified building blocks, plus a small model that translates plain
English into that vocabulary.

Start with [`docs/REVIEW.md`](docs/REVIEW.md) (one-page honest summary, the claims we do not make, open items), then
[`docs/WHAT-WE-LEARNED.md`](docs/WHAT-WE-LEARNED.md) (findings, with retractions). The scoreboard of all 32 experiments ("swings")
and their kill rules is [`docs/SWINGS.md`](docs/SWINGS.md); gate status is [`gates/STATUS.md`](gates/STATUS.md).

## The demo: who sits next to whom at the White House AI lunch

`demo/luncheon/index.html` is a single static page built around the 34-seat chart that was posted for a White House AI luncheon
(transcribed by hand into `data/hero/luncheon.json`). Its seating rules in English were read beforehand by a fine-tuned
Qwen3-1.7B (LoRA; the HERO-6 adapter, `runs/hero6/page_outputs.json`). Each became a short program in "stage words" (`size`,
`together`, `limit`, `apart`, `order`, plus `avoid`/`pair` for named guests and companies). The page then seats the real chart, and an unbounded grid of synthetic rooms, with a JavaScript port of the
checked seating function. It also shows what an untuned small chatbot does with the same rule.

```sh
python3 -m http.server 8765 --directory demo/luncheon    # then open http://localhost:8765
node demo/luncheon/test_seating.js                       # JS port vs the Python reference
python3 demo/luncheon/build.py                           # rebuild index.html from template.html + seating.js + app.js
```

Read the fine print before quoting it:
- **The page does not run a model.** The model's readings were recorded ahead of time. The browser runs only the seating program.
- It is a game. The rules are the host's rules. Nothing on the page claims the guests hold these views, feuds or seats.
- "Verified" covers the net, not the model's reading. A misread sentence still produces a valid arrangement, just for the wrong
  rule (about 1% on our test set, 9% on an independently written one). That is why the page always shows the parsed program.
- Seating 100,000 guests works and is exact, but depth is linear: the next-fit seating stage is sequential. It shows exactness and
  cost. It does not show parallelism.

### HERO-6 note (2026-09-30): rules that name guests

HERO-6 retrained the 1.7B model to read rules that name guests or companies (`avoid X Y`, `pair X Y`). Verdict: **partial pass**.
On the new, independently written named-guest set it scores 89.2% pass@1 (85.0% under the strict judge; the bar was 85%). But it
regressed on HERO-1's set 1 from 98.6% to 93.1%, beyond the 3-point limit the kill rule allowed. The new words collide with old
wording ("pairs only, please" now loses its `size 2`). `avoid` now runs inside the verified net (seeds 0-2 pass). Details in
[`docs/HERO-6.md`](docs/HERO-6.md). Agent-reported, not yet re-run by the lead.

## Results that held up

Numbers come from the docs named in each row. "Checked" means the lead re-ran or audited them. "Agent" means they come from the
experiment agent's own report and result files and have not been independently re-run yet (see [Provenance](#provenance)).

| Result | Number | Source | Checked by |
|---|---|---|---|
| Frozen frontier models write correct nets | G0 20/20; G1 seed 0: native 176/200, Bend 189/200 | `gates/g0/REPORT.md`, `gates/STATUS.md` | Checked |
| Machine-applied K-cell lookahead (a medium-specific trick Bend's `match` can't express) | 51/76 nets transformed, 232/232 pass seeds 0-2, median depth -43.5% | `docs/LOOKAHEAD.md` | Agent, 8/8 spot-checked on fresh seeds |
| Verified library composition lifts weak authors | typed glue: Haiku 2/10 to 6/10; recipes: 1/16 to 10/16 (p = 0.006) | `docs/TYPED-GLUE.md`, `docs/RECIPES.md` | Agent |
| HERO-1: English rule -> 1.7B model -> verified program | 98.6% on the designer's 72 rules, 90.6% on an independently written 72; untuned local chatbot breaks a rule in 88% of answers, pipeline in 0% | `docs/HERO-1.md` | Agent; the demo's JS port vs the Python reference checked by the lead |
| HERO-2: equivalence proofs by normalization | 91/92 known-equal pairs proved, 0 false proofs on 46 unequal (scope: plumbing and inlining) | `docs/HERO-2.md` | Agent |
| HERO-3: verified auto-parallelizer | depth exponent 0.11 vs 1.0 on tree input (needs a caller-supplied balanced tree) | `docs/HERO-3.md` | Agent |
| HERO-5: exact explanations by counterfactual re-execution | 100/100 (the trace itself scored 0/100, see below) | `docs/HERO-5.md` | Agent |

## Results that didn't (said plainly)

| Claim we hoped to make | What happened | Source |
|---|---|---|
| Native nets beat a human-language route | With equal author effort, Bend ties on graph/reconciliation programs: 87 programs, depth Bend/native geomean 0.55x, native shallower on 39, Bend on 48; native does ~22% less work at the median. The earlier "3-107x" was an author effect and is retracted. | `docs/BEND-FAIR-BASELINE.md`, `runs/exp17` |
| Gate 1 (pre-registered) | Not passed: 88% native vs a 90% bar, seed 0 only. Seeds 1-2 never run. | `gates/g1/prereg.md`, `gates/STATUS.md` |
| G4: faster than the human route at 100k | Not met. A strong-Bend reconciliation is within 1.34x of native, and plain union-find is ~3,650x faster than either net. | `docs/RECON-BEND.md`, `docs/RECON-REALDATA.md` |
| Small models fine-tuned to write whole nets | 14-31% vs 47-88% for Bend. Stage-level factorization works, but only on a vocabulary we designed; unseen wording 43-78%. | `docs/STAGE-FACTORIZATION.md` |
| Constrained decoding / repair / factorized wiring fix the failures | All killed; the model's mistakes are structural | `docs/SWINGS.md` |
| Growing a vocabulary by prompt alone (HERO-4) | 6/10 new words, with crowding (-9 pts on base words); retraining fixes it (10/10) | `docs/HERO-4.md` |
| Superposition (HVM4) speeds up synthesis | No. Plain enumeration with observational-equivalence merging wins, and that is a known technique | `docs/WHAT-WE-LEARNED.md` |
| Explanations read off the reduction trace (HERO-5) | 0/100 exact | `docs/HERO-5.md` |

Also: every pass rate above is internal. The 200-program corpus and its hidden suites were written by us. No external benchmark
has been run yet (candidates are listed in `docs/REVIEW.md`, section 7).

## Repository layout

| Path | What |
|---|---|
| `CHARTER.md`, `PHYSICS.md`, `BEND_PRIMER.md` | Project charter and the frozen primers given to model authors (byte-identical to the originals; results depend on them) |
| `genome/` | The harness: `types` (encodings), `executor` (runs HVM2), `verify` (hidden-suite verifier), `corpus/` (200 frozen programs, `MANIFEST.json`), `contract`, `opt`, `induce`, `lib/`, and one folder per experiment (`exp*`, `hero1`-`hero6`) |
| `gates/` | Pre-registrations and gate reports (`gates/g1/prereg.md` is frozen) |
| `docs/` | One write-up per swing/hero experiment, plus `REVIEW.md`, `WHAT-WE-LEARNED.md`, `SWINGS.md`, `METHODOLOGY-REVIEW.md` |
| `runs/` | Verified nets (`.hvm`, `.bend`), result/summary JSON and logs from the runs |
| `demo/luncheon/` | The demo page source and its test |
| `data/hero/` | The luncheon chart transcription and the frozen HERO-1/HERO-6 test sets |
| `patches/hvm2-depth.patch` | Our only change to HVM2: a round-by-round scheduler that reports parallel depth (same rewrite rules) |
| `scripts/` | `setup_physics.sh` (fetch + build pinned runtimes), `check_release.sh` (secret scan + size report) |
| `adapters/` | Empty; see `adapters/README.md` for the LoRA weights |

## Reproduce

Tested on macOS on Apple silicon. Linux should work for everything except the MLX model scripts.

**1. Runtimes** (needs git, a Rust toolchain, clang). Fetches HVM2 v2.0.22 at `6542760`, builds it, builds a second copy with the
depth patch, fetches HVM4 at `6defdfc`, installs Bend 0.2.38 with cargo, and builds the HERO-5 tracer. Nothing is vendored except the
tracer.

```sh
scripts/setup_physics.sh            # --no-hvm4 / --no-bend to skip those
```

**2. Python.** The harness uses only the standard library (Python 3.10+ should work; we ran 3.14). Optional extras:
`pip install mlx-lm` (Apple silicon only; to run the models, which also need `adapters/`), `numpy` (exp11), `torch networkx` (exp4).
Run everything from the repo root.

**3. Run the verifier.**

```sh
python3 -m genome.corpus.check                                        # corpus contract self-check (200 programs)
python3 -m genome.verify t1_max runs/g0/t1_max/attempt_1.hvm          # one G0 net against its hidden suite
python3 -m genome.verify t1_max runs/g0/t1_max/attempt_1.hvm --seed 3 # fresh seed
python3 -m genome.hero1.sectioner 0 1 2                               # the demo's seating net, seeds 0-2
```

**4. The demo:** see above. `node demo/luncheon/test_seating.js` checks 1,000 random cases plus the five recorded readings against
the Python reference.

What is not here: the model weights (`adapters/README.md`), the regenerable training sets (`genome/hero1/gen_train.py` and friends
rebuild them), raw sample dumps over 2 MB, the OpenSanctions file and anything listing its entities (see below), and the scratch
directory.

## Provenance

Most of this work was carried out by AI agents (Claude models) under a lead agent, with the owner setting direction. Each
experiment pre-registered a kill rule before looking at results. That discipline is why the negative table above is as long as it is.

- **Re-run or audited by the lead:** G0; the first 4 swing-8 nets at 64x input; 8 swing-18 nets on fresh seeds; the fair-Bend
  comparison recomputed from result files; exp19 (12/12 on fresh seeds 3-4); the demo's seating function vs the Python reference
  (400/400 random cases plus the five recorded arrangements).
- **Agent-reported only:** HERO-1 to HERO-5, swings 20-27 unless noted, the 87-program Bend swarm's own verification logs, and
  swing 21. These numbers come from the agents' reports and result files and have not yet been independently re-run.
- **HERO-6** (named guests: `avoid`, `pair`): agent-reported, see the note above. The demo's JS port, now with `pair`, passes
  `test_seating.js` in this copy.
- Re-checked while preparing this copy: corpus check 200/200, the G0 `t1_max` net passes, the demo sectioner net passes seed 0
  (101/101), and `test_seating.js` passes. This used freshly built runtimes from `scripts/setup_physics.sh`.
- Run records under `runs/` are kept as they were written, except that the original home directory in absolute paths is replaced
  by `<home>`. Code under `genome/` and `demo/` was changed only to use repo-relative paths.

### Data

- `data/hero/luncheon.json` is a hand transcription of a publicly posted seating chart. The chart image itself is not included.
- The real-data reconciliation runs (swings 20 and 27) used the OpenSanctions pairs file (CC BY-NC 4.0, research use only). It is
  **not** included. Neither is any derived list of entity ids or names. What remains under `runs/exp16` and `runs/exp21` is nets
  and aggregate statistics: counts, depths, timings, cluster-size histograms. To reproduce them, download the file yourself under its
  license into `data/opensanctions/` (`genome/exp16/data.py` names the expected path).

## License

Apache-2.0 (`LICENSE`), **pending the owner's confirmation**. Third-party code keeps its own license. HVM2/HVM4/Bend are fetched,
not vendored, except `genome/hero5/tracer`, a modified HVM2 (Apache-2.0).
