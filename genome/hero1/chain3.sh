#!/bin/zsh
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
while kill -0 42275 2>/dev/null; do sleep 5; done
BASE_MODEL=mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit BASE_OUT=runs/hero1/baseline30b_samples.json python3 -m genome.hero1.baseline score > runs/hero1/baseline30b_score.txt
./genome/hero1/extras2.sh
BASE_COT=1 BASE_N=4 BASE_OUT=runs/hero1/baseline4b_cot_samples.json $PY -m genome.hero1.baseline sample
BASE_COT=1 BASE_OUT=runs/hero1/baseline4b_cot_samples.json python3 -m genome.hero1.baseline score > runs/hero1/baseline4b_cot_score.txt
echo chain3 done
