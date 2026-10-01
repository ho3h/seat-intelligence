#!/bin/zsh
# extras (GPU, one job at a time): zero-shot controls with the vocabulary in the prompt; stronger / reasoning chatbot baselines.
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
mkdir -p runs/hero1/samples
$PY -m genome.hero1.sample --model mlx-community/Qwen3-4B-Instruct-2507-4bit --vocab --set data/hero/policies_test.json --n 5 --temp 0.7 --max-tokens 120 --out runs/hero1/samples/zs4b_t07.json || exit 1
$PY -m genome.hero1.sample --model mlx-community/Qwen3-1.7B-4bit --vocab --set data/hero/policies_test.json --n 5 --temp 0.7 --max-tokens 120 --out runs/hero1/samples/zs1p7b_t07.json || exit 1
python3 -m genome.hero1.evaluate runs/hero1/samples/zs4b_t07.json > /dev/null
python3 -m genome.hero1.evaluate runs/hero1/samples/zs1p7b_t07.json > /dev/null
BASE_MODEL=mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit BASE_OUT=runs/hero1/baseline30b_samples.json BASE_N=20 $PY -m genome.hero1.baseline sample || exit 1
BASE_MODEL=mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit BASE_OUT=runs/hero1/baseline30b_samples.json python3 -m genome.hero1.baseline score > runs/hero1/baseline30b_score.txt
BASE_COT=1 BASE_N=5 BASE_OUT=runs/hero1/baseline4b_cot_samples.json $PY -m genome.hero1.baseline sample || exit 1
BASE_COT=1 BASE_OUT=runs/hero1/baseline4b_cot_samples.json python3 -m genome.hero1.baseline score > runs/hero1/baseline4b_cot_score.txt
echo extras done
