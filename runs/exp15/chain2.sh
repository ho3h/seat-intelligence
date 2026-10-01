#!/bin/zsh
# GPU chain 2 (one MLX job at a time). 0.6B and 4B diverged at lr 2e-4 (loss spikes at iter 25-50): rerun at 5e-5.
cd <home>/Genome
genome/exp15/train.sh 0p6b_lr5e5 mlx-community/Qwen3-0.6B-4bit 600 5e-5 > runs/exp15/train_0p6b_lr5e5.log 2>&1
genome/exp15/eval.sh 0p6b_lr5e5 mlx-community/Qwen3-0.6B-4bit > runs/exp15/eval_0p6b_lr5e5.log 2>&1
until [ -f runs/exp15/data_aug/train.jsonl ]; do sleep 10; done
genome/exp15/train.sh 1p7b_aug mlx-community/Qwen3-1.7B-4bit 600 2e-4 runs/exp15/data_aug > runs/exp15/train_1p7b_aug.log 2>&1
genome/exp15/eval.sh 1p7b_aug mlx-community/Qwen3-1.7B-4bit > runs/exp15/eval_1p7b_aug.log 2>&1
genome/exp15/train.sh 4b_lr5e5 mlx-community/Qwen3-4B-4bit 600 5e-5 > runs/exp15/train_4b_lr5e5.log 2>&1
genome/exp15/eval.sh 4b_lr5e5 mlx-community/Qwen3-4B-4bit > runs/exp15/eval_4b_lr5e5.log 2>&1
echo CHAIN2 DONE
