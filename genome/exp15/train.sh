#!/bin/zsh
# exp15 LoRA: same data and recipe for every size. usage: genome/exp15/train.sh <tag> <hf model> [iters]
# e.g. genome/exp15/train.sh 1p7b mlx-community/Qwen3-1.7B-4bit 600 2e-4 runs/exp15/data
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
TAG=$1; MODEL=$2; ITERS=${3:-600}; LR=${4:-2e-4}; DATA=${5:-runs/exp15/data}
if pgrep -f "python.* -m mlx_lm" > /dev/null; then echo "another MLX job is running"; exit 1; fi
$PY -m mlx_lm lora --model $MODEL --train --data $DATA --iters $ITERS --batch-size 8 --num-layers -1 \
  --learning-rate $LR --mask-prompt --steps-per-report 25 --steps-per-eval 200 --val-batches 10 --save-every 1000 \
  --adapter-path adapters/exp15_$TAG --seed 0
