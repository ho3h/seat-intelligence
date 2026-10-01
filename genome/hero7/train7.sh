#!/bin/zsh
# HERO-7 LoRA. usage: genome/hero7/train7.sh <tag> <hf model> <batch> <iters> [data]
# Recipe as HERO-1/6: LoRA all layers (rank 8 default), lr 5e-5, prompt masked, seed 0.
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
TAG=$1; MODEL=$2; BS=$3; ITERS=$4; DATA=${5:-runs/hero7/data}
$PY -m mlx_lm lora --model $MODEL --train --data $DATA --iters $ITERS --batch-size $BS --num-layers -1 \
  --learning-rate 5e-5 --mask-prompt --steps-per-report 25 --steps-per-eval 300 --val-batches 10 --save-every 300 \
  --max-seq-length 384 --adapter-path adapters/hero7_$TAG --seed 0
