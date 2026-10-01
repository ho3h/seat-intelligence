#!/bin/zsh
# uniform recipe for the size table: 1.7B at lr 5e-5 too
cd <home>/Genome
until grep -q "CHAIN4 DONE" runs/exp15/chain4.log; do sleep 20; done
genome/exp15/train.sh 1p7b_lr5e5 mlx-community/Qwen3-1.7B-4bit 600 5e-5 > runs/exp15/train_1p7b_lr5e5.log 2>&1
genome/exp15/eval.sh 1p7b_lr5e5 mlx-community/Qwen3-1.7B-4bit > runs/exp15/eval_1p7b_lr5e5.log 2>&1
echo CHAIN5 DONE
