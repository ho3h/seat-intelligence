# adapters/ (not in this repo)

The LoRA adapters are about 1 GB in total, so they are not committed. They will be published separately on a model hub;
the link goes here once they are up. Until then, ask the repo owner.

Place each adapter directory here under the name below; the scripts look for `adapters/<name>/adapters.safetensors`
(MLX `mlx_lm lora` format, with its `adapter_config.json`).

| Name | Base model | What it is | Used by |
|---|---|---|---|
| `hero6_1p7b` | `mlx-community/Qwen3-1.7B-4bit` | **The adapter the demo uses** (HERO-6): English seating rule, including named guests and companies (`avoid`, `pair`), -> stage-word program | `genome/hero6/*`, the recorded page sentences in `runs/hero6/page_outputs.json` |
| `hero1_1p7b` | `mlx-community/Qwen3-1.7B-4bit` | HERO-1 model (six stage words, no names); produced the original five showcase readings | `genome/hero1/*`, `runs/hero1/showcase.json` |
| `hero4_main`, `hero4_const`, `hero4_retrain` | `mlx-community/Qwen3-1.7B-4bit` | HERO-4 vocabulary-growth runs | `genome/hero4/*` |
| `exp15_*` | `mlx-community/Qwen3-{0.6B,1.7B,4B}-4bit` | Stage-level factorization (swing 21) | `genome/exp15/*` |
| `native_v1`, `native_ei1`, `bend_v1`, `exp4_skel` | `mlx-community/Qwen3-4B-Instruct-2507-4bit` | Early whole-net fine-tunes and the skeleton model (negative results) | `genome/exp*`, `genome/local_eval.py` |
| `f1_1p7b` | `mlx-community/Qwen3-1.7B-4bit` | Early whole-net fine-tune (negative result) | `genome/local_eval.py` |

You do not need any adapter to run the verifier, the corpus checks, or the demo page: the page replays sentences the model read
beforehand and runs only the seating program in the browser. To retrain instead of downloading, regenerate the training data
(`genome/hero1/gen_train.py`, `genome/hero6/gen_train6.py`) and run `genome/hero1/train.sh` with an MLX-capable Python in `PY`.
