#!/bin/zsh
# after extras.sh: test set 2 (external author) + larger-n robustness run on test set 1
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
M=mlx-community/Qwen3-1.7B-4bit; A=adapters/hero1_1p7b
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test2.json --n 5 --temp 0.7 --seed 2 --out runs/hero1/samples/test2_t07.json || exit 1
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test2.json --n 1 --temp 0.0 --out runs/hero1/samples/test2_greedy.json || exit 1
TEST_FILE=data/hero/policies_test2.json python3 -m genome.hero1.evaluate runs/hero1/samples/test2_t07.json > runs/hero1/samples/test2_t07.eval.txt
TEST_FILE=data/hero/policies_test2.json python3 -m genome.hero1.evaluate runs/hero1/samples/test2_greedy.json > runs/hero1/samples/test2_greedy.eval.txt
TEST_FILE=data/hero/policies_test2.json python3 -m genome.hero1.taxonomy runs/hero1/samples/test2_t07.scored.json > /dev/null
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test.json --n 20 --temp 0.7 --seed 3 --out runs/hero1/samples/test_t07_n20.json || exit 1
python3 -m genome.hero1.evaluate runs/hero1/samples/test_t07_n20.json > runs/hero1/samples/test_t07_n20.eval.txt
python3 -m genome.hero1.taxonomy runs/hero1/samples/test_t07_n20.scored.json > /dev/null
echo extras2 done
