# Hero example: the "Super Intelligence Luncheon" seating problem

Status: defined 2026-09-30. Read by the five last-ditch experiments (runs/hero1..5). Data: `data/hero/luncheon.json` (34 seats, hand-transcribed from `data/hero/luncheon_chart.jpg`, the chart posted for the White House luncheon of 2026-09-29).

## Why this is the hero
Everyone has faced a seating chart. Ours is the real one: 34 named guests at a two-sided long table (17 per side, POTUS facing VPOTUS). The public pitch:
"Say your seating rule in one sentence. A tiny local model turns it into a program. The program seats 34 or 100,000 guests, never breaks a rule, and can say why each guest sits where they do."

## Mapping to what we already have (verified nets exist for these kernels)
| Seating | Kernel |
|---|---|
| Guests who belong together (same company; chain of "sits with") | transitive clusters (t5 clustering kernels) |
| "Never in the same section" | must-not-link (t5_conflict_greedy) |
| Section size limit (a section is a run of about 6 adjacent seats) | capped clusters (t5_conflict_greedy_cap, t5_decide_stage_cap) |
| Who is placed first when rules collide | ordered greedy tie-break |
| Section captain | canonical id |

A long table is a line, so we use SECTIONS: split the table into contiguous sections of at most 6 seats and decide which guests share a section. Ordering inside a section is a second, simple stage.

## Rules must be defined by the player, not asserted about real people
These are real people. NEVER invent or imply personal feuds, dislikes or relationships. Allowed inputs to any rule: the printed company or title on the chart, and the coarse `category` field in `luncheon.json` (ai_lab, big_tech, chips, software_security, investor, government, unlabelled). Rules are the HOST'S RULES in a game, e.g. "keep colleagues from the same company together", "no two guests from competing AI labs in one section", "no more than 2 government officials per section", "put chip makers next to AI labs". Everything is labelled as a game, not a claim about the guests. Do not guess affiliations for the 6 `unlabelled` guests.

## Baseline facts worth showing (from the chart itself, no opinions)
- As posted: 3 ai_lab guests (Brockman OpenAI; Amodei and Brown Anthropic), Palantir has 2 (Sankar left row 1, Karp left row 13), Anthropic has 2 (Amodei right row 2, Brown left row 16).
- Any rule can be scored against the posted arrangement (how many rule violations the posted chart has) as a neutral metric.

## Ground rules for every agent (from the whole program)
- No OpenRouter, no paid APIs. Local compute only (an MLX Python venv, read-only) plus your own reasoning.
- Do not modify frozen artifacts (PHYSICS.md, BEND_PRIMER.md, corpus MANIFEST, gates/g1/prereg.md). New work goes in your own dir.
- Never run `pkill -f hvm` or kill processes you did not start.
- Write your kill rule and your test set BEFORE looking at results, and put them in your doc's first section. Report exact denominators. Report negatives plainly.
- Keep concurrent processes modest (machine is shared with other agents). Cap yourself at 4 heavy processes.
- Never read or print the project .env file.
- Hand back a SHORT plain-language report: verdict against your kill rule, the key numbers with denominators, caveats, and file paths. Add one dated bullet to gates/STATUS.md and one row/update in docs/SWINGS.md (rows 28-32).

## The page (2026-09-30)
`demo/luncheon/index.html` (built by `demo/luncheon/build.py` from `template.html`, `seating.js`, `app.js`; data from `data/hero/luncheon.json` and `runs/hero1/showcase.json`). Canvas page in the style of the posted chart: the East Room with the real 34 seats, then an unbounded grid of identical rooms with synthetic guests (seeded per table, created on demand). Five recorded sentences were read by the tuned 1.7B model beforehand; the page does not run a model. It re-runs the seating function, a line-for-line JS port of `genome/hero1/lang.py`, checked by `demo/luncheon/test_seating.js` against 400 random cases from the Python reference and the five showcase arrangements. Serve with `python3 -m http.server 8765 --directory demo/luncheon` (also in `.claude/launch.json` as "luncheon").
