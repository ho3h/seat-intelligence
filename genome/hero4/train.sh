#!/bin/zsh
# HERO-4 LoRA: usage genome/hero4/train.sh <tag> <hf model> <iters> <lr> <data dir>
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
TAG=$1; MODEL=$2; ITERS=${3:-600}; LR=${4:-5e-5}; DATA=${5:-runs/hero4/data}
while pgrep -f "python.* -m mlx_lm lora" > /dev/null; do echo "waiting: another MLX training runs"; sleep 30; done
$PY -m mlx_lm lora --model $MODEL --train --data $DATA --iters $ITERS --batch-size 8 --num-layers -1 \
  --learning-rate $LR --mask-prompt --steps-per-report 25 --steps-per-eval 200 --val-batches 10 --save-every 1000 \
  --max-seq-length 2048 --adapter-path adapters/hero4_$TAG --seed 0
