#!/bin/zsh
# sample iid / deep / para sets for one adapter (GPU, one MLX job at a time). usage: genome/exp15/eval.sh <tag> <hf model>
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
TAG=$1; MODEL=$2
while pgrep -f "python.* -m mlx_lm lora" > /dev/null; do sleep 20; done
for S in iid deep para novel; do
  $PY -m genome.exp15.sample --model $MODEL --adapter adapters/exp15_$TAG --set runs/exp15/sets/$S.json --n 4 \
      --out runs/exp15/samples/${TAG}_$S.json || exit 1
done
