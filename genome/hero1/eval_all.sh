#!/bin/zsh
# after training: scale test (CPU), then sampling + judging. usage: genome/hero1/eval_all.sh
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
M=mlx-community/Qwen3-1.7B-4bit; A=adapters/hero1_1p7b
mkdir -p runs/hero1/samples
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test.json --n 5 --temp 0.7 --out runs/hero1/samples/test_t07.json || exit 1
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test.json --n 1 --temp 0.0 --out runs/hero1/samples/test_greedy.json || exit 1
$PY -m genome.hero1.sample --model $M --adapter $A --set runs/hero1/valid_set.json --n 1 --temp 0.0 --out runs/hero1/samples/valid_greedy.json || exit 1
IDS=$(python3 -c "
import sys; sys.path.insert(0,'.')
from genome.hero1.baseline import selected
print(','.join(p['id'] for p in selected()))")
$PY -m genome.hero1.sample --model $M --adapter $A --set data/hero/policies_test.json --ids $IDS --n 20 --temp 0.7 --seed 1 --out runs/hero1/samples/base20_t07.json || exit 1
python3 -m genome.hero1.evaluate runs/hero1/samples/test_t07.json > runs/hero1/samples/test_t07.eval.txt
python3 -m genome.hero1.evaluate runs/hero1/samples/test_greedy.json > runs/hero1/samples/test_greedy.eval.txt
python3 -m genome.hero1.taxonomy runs/hero1/samples/test_t07.scored.json > /dev/null
$PY -m genome.hero1.showcase > runs/hero1/showcase.log 2>&1
echo eval done
