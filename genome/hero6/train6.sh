#!/bin/zsh
# HERO-6 LoRA: HERO-1 recipe (Qwen3-1.7B-4bit, LoRA all layers, lr 5e-5, prompt masked, seed 0) on runs/hero6/data.
# Batch 16 x 900 iters (14,400 examples, about 1.3 epochs of 11,000) instead of 8 x 1,200 (speed; same examples seen order of magnitude).
cd "$(dirname "$0")/../.."
PY="${PY:-python3}"  # an MLX-capable Python (mlx_lm)
if pgrep -f "python.* -m mlx_lm" > /dev/null; then echo "another MLX job is running"; exit 1; fi
$PY -m mlx_lm lora --model mlx-community/Qwen3-1.7B-4bit --train --data runs/hero6/data --iters ${ITERS:-900} --batch-size 16 --num-layers -1 \
  --learning-rate 5e-5 --mask-prompt --steps-per-report 25 --steps-per-eval 450 --val-batches 10 --save-every 450 \
  --max-seq-length 384 --adapter-path adapters/hero6_1p7b --seed 0
