#!/bin/zsh
# GPU chain (one MLX job at a time): eval 1.7B, then train+eval 0.6B, then train+eval 4B
cd /Users/tedsandtads/Genome
while pgrep -f "mlx_lm lora" > /dev/null; do sleep 15; done
genome/exp15/eval.sh 1p7b mlx-community/Qwen3-1.7B-4bit > runs/exp15/eval_1p7b.log 2>&1
genome/exp15/train.sh 0p6b mlx-community/Qwen3-0.6B-4bit 600 > runs/exp15/train_0p6b.log 2>&1
genome/exp15/eval.sh 0p6b mlx-community/Qwen3-0.6B-4bit > runs/exp15/eval_0p6b.log 2>&1
genome/exp15/train.sh 4b mlx-community/Qwen3-4B-4bit 600 > runs/exp15/train_4b.log 2>&1
genome/exp15/eval.sh 4b mlx-community/Qwen3-4B-4bit > runs/exp15/eval_4b.log 2>&1
echo CHAIN DONE
