#!/bin/zsh
# HERO-1 LoRA (same recipe family as exp15). usage: genome/hero1/train.sh <tag> <hf model> [iters] [lr]
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
TAG=$1; MODEL=$2; ITERS=${3:-1200}; LR=${4:-5e-5}; DATA=${5:-runs/hero1/data}
if pgrep -f "python.* -m mlx_lm" > /dev/null; then echo "another MLX job is running"; exit 1; fi
$PY -m mlx_lm lora --model $MODEL --train --data $DATA --iters $ITERS --batch-size 8 --num-layers -1 \
  --learning-rate $LR --mask-prompt --steps-per-report 25 --steps-per-eval 200 --val-batches 10 --save-every 400 \
  --max-seq-length 1024 --adapter-path adapters/hero1_$TAG --seed 0
