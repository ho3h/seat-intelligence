# HERO-7: a stronger tiny seating model (2026-10-01)

**Outcome.** A retrained Qwen3-1.7B (LoRA, `adapters/hero7_r7_1p7b_b16`) reads 89 of 100 fresh rules exactly right on one try
(STRICT judge), up from 79 for the HERO-6 model, and 442 of 500 readings at T = 0.7 (88.4%, up from 78.4%). A 4B model trained the same
way scores within about a point, so the 1.7B replaced HERO-6 on the demo page and on Hugging Face
([hopski/seat-intelligence-1.7b](https://huggingface.co/hopski/seat-intelligence-1.7b), v2).

## 1. Test protocol

**Fresh test set (set 7).** `data/hero/policies_test7.json`, sha256 `8297061510eda10400833341362a05cbd42f85cb9276e1f5cd4fa91c69250d2a`.
100 requests written by a separate subagent that saw only the guest list and the plain meaning of the instruction words
(`data/hero/policies_test7_raw.json`); the gold program for each was written before any HERO-7 model existed (`genome/hero7/make_test7.py`,
which refuses to overwrite). Some requests name guests "added on the spot" who are not on the chart.

**Judge.** `genome/hero7/judge7.py` (sha256 `770c46e1e2d7426178babd6923c58d40080e5bdcd771b2fdbf6ccb49b4a482be`): the HERO-6 three-list
criterion (lenient) and STRICT = lenient and the same seating as the gold on 100 probe lists. STRICT is the headline. Sets 1 and 2 use
the unchanged HERO-1 judge; set 6 uses `genome/hero6/judge6.py`. Scoring: `genome/hero7/score7.py`; grid runner: `genome/hero7/eval7.py`.

**Which numbers are clean.** Set 7 is the only set no earlier round had seen. Sets 1, 2 and 6 were looked at while earlier models were
built and their failures shaped HERO-7's extra data (terse phrasings, rarer rules), so their gains are probably a little flattering.

## 2. Training data (`genome/hero7/gen_train7.py`, `runs/hero7/data_meta.json`)

15,912 training sentences and 300 for validation, from five sources: the HERO-6 set (8,948 kept), replayed earlier examples (3,222),
terse phrasings (1,676), coverage of rarer rules (1,560) and paraphrases (506). Paraphrases were written by a larger LOCAL model
(Qwen3-30B-A3B-Instruct-2507, MLX 4-bit; `genome/hero7/para7.py`) from HERO-6 training sentences only, and kept only if every name and
number survived (735 of 1,600 kept before deduplication). Every sentence that equals a test text from sets 1, 2, 6 or 7 after
normalisation, or shares any six-word sequence with one, was dropped (2,911 dropped in all; `genome/hero7/overlap7.py`).

## 3. Runs

Same recipe as HERO-1 and HERO-6 (`genome/hero7/train7.sh`: LoRA on all layers, rank 8, scale 20, learning rate 5e-5, prompt masked,
seed 0, maximum length 384):

- `r7_1p7b_b8`: Qwen3-1.7B-4bit, batch 8, 1,200 iterations, final validation loss 0.012. Not evaluated on any test set.
- `r7_1p7b_b16`: Qwen3-1.7B-4bit, batch 16, 900 iterations, final validation loss 0.002. Picked over `b8` on validation loss alone,
  before either saw a test set.
- `r7_4b_b16`: Qwen3-4B-4bit, batch 16, 600 iterations.

## 4. Results (`runs/hero7/grid/*.json`, logs `runs/hero7/eval_*.log`)

Pass rates: one greedy try per rule, or five tries per rule at T = 0.7 counted individually. Constrained decoding
(`genome/hero7/constrain7.py`) only lets the model write valid instruction words and known names.

**plain decoding** (sets 7 and 6: STRICT; sets 1 and 2: the HERO-1 judge)

| Model | set 7, greedy | set 7, T=0.7 x5 | set 6, T=0.7 x5 | set 1, T=0.7 x5 | set 2, T=0.7 x5 |
|---|---|---|---|---|---|
| HERO-6 1.7B (v1, the old page model) | 79/100 (79.0%) | 392/500 (78.4%) | 309/360 (85.8%) | 334/360 (92.8%) | 315/360 (87.5%) |
| HERO-7 1.7B, batch 16 (v2, now on the page and Hugging Face) | 89/100 (89.0%) | 442/500 (88.4%) | 336/360 (93.3%) | 355/360 (98.6%) | 325/360 (90.3%) |
| HERO-7 4B, batch 16 | 90/100 (90.0%) | 448/500 (89.6%) | 339/360 (94.2%) | 347/360 (96.4%) | 339/360 (94.2%) |

**constrained decoding** (sets 7 and 6: STRICT; sets 1 and 2: the HERO-1 judge)

| Model | set 7, greedy | set 7, T=0.7 x5 | set 6, T=0.7 x5 | set 1, T=0.7 x5 | set 2, T=0.7 x5 |
|---|---|---|---|---|---|
| HERO-6 1.7B (v1, the old page model) | 82/100 (82.0%) | 403/500 (80.6%) | 319/360 (88.6%) | 339/360 (94.2%) | 320/360 (88.9%) |
| HERO-7 1.7B, batch 16 (v2, now on the page and Hugging Face) | 90/100 (90.0%) | 451/500 (90.2%) | 339/360 (94.2%) | 355/360 (98.6%) | 338/360 (93.9%) |
| HERO-7 4B, batch 16 | 92/100 (92.0%) | 448/500 (89.6%) | 350/360 (97.2%) | 347/360 (96.4%) | 345/360 (95.8%) |

Majority voting over the five T = 0.7 tries gave no consistent gain over one greedy try (within two rules either way on every set and model), so it is not used.

## 5. What changed on the page and on Hugging Face

- The page's recorded readings (`runs/hero7/page_outputs_r7_1p7b.json`, plain decoding, `genome/hero7/page7.py`) come from the new
  model: 12 of the 13 page sentences match their intended programs (HERO-6: 10). The one miss turns "software and security firms
  together" into `limit software_security 2`; the page shows it as its "Where it can go wrong" example.
- The "other timelines" now use set 7: 500 readings (100 fresh rules, five tries each), 442 correct under STRICT
  (`runs/hero7/readings_set7_r7_1p7b.json`). They used set 6 before (321 of 360, lenient).
- Hugging Face: `adapters.safetensors` and `adapter_config.json` replaced; the model card's example still prints exactly
  `avoid Elon_Musk OpenAI` / `avoid Elon_Musk Mark_Zuckerberg`. v1 stays in that repository's history.

## 6. Where it still goes wrong (set 7, greedy, STRICT: 11 misses)

- Six involve "White House staff", a group the chart never labels (those guests are `unlabelled`); it writes `government` or invents a category.
- Three involve guests added on the spot who are not on the chart; it mixes up which name goes with which company.
- One picks the wrong guest ("Arora apart from Daniels" became Director Clayton).
- One shorthand ("Palantir duo: same section") names the company instead of its two guests.

## 7. Reproduce

```sh
PY=/path/to/mlx/python genome/hero7/train7.sh r7_1p7b_b16 mlx-community/Qwen3-1.7B-4bit 16 900
$PY -m genome.hero7.eval7 mlx-community/Qwen3-1.7B-4bit adapters/hero7_r7_1p7b_b16 R7_1p7b_b16
$PY -m genome.hero7.page7 mlx-community/Qwen3-1.7B-4bit adapters/hero7_r7_1p7b_b16 plain 0 runs/hero7/page_outputs_r7_1p7b.json
```

The training data itself is not in the repository; regenerate it with `genome/hero7/gen_train7.py` (paraphrases need
`genome/hero7/para7.py` and a local 30B model).
