#!/bin/zsh
# HERO-6 evaluation chain (after training). Sampling: genome/hero1/sample.py (same prompt as HERO-1).
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
A=adapters/hero6_1p7b; M=mlx-community/Qwen3-1.7B-4bit; O=runs/hero6/samples; mkdir -p $O
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test6.json --n 5 --temp 0.7 --seed 0 --out $O/test6_t07.json &
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test.json --n 5 --temp 0.7 --seed 0 --out $O/test_t07.json &
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test2.json --n 5 --temp 0.7 --seed 0 --out $O/test2_t07.json &
wait
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test6.json --n 1 --temp 0 --out $O/test6_greedy.json &
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test.json --n 1 --temp 0 --out $O/test_greedy.json &
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test2.json --n 1 --temp 0 --out $O/test2_greedy.json &
wait
$PY -m genome.hero6.page6 $A runs/hero6/page_outputs.json
echo EVAL_SAMPLING_DONE
