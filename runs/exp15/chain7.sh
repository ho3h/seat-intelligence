#!/bin/zsh
# after chain3: uniform-recipe 1.7B (lr 5e-5), wording-augmented 1.7B (lr 5e-5), then the zero-shot vocabulary control
cd <home>/Genome
until grep -q "CHAIN3 DONE" runs/exp15/chain3.log; do sleep 20; done
genome/exp15/train.sh 1p7b_lr5e5 mlx-community/Qwen3-1.7B-4bit 600 5e-5 > runs/exp15/train_1p7b_lr5e5.log 2>&1
genome/exp15/eval.sh 1p7b_lr5e5 mlx-community/Qwen3-1.7B-4bit > runs/exp15/eval_1p7b_lr5e5.log 2>&1
genome/exp15/train.sh 1p7b_aug_lr5e5 mlx-community/Qwen3-1.7B-4bit 600 5e-5 runs/exp15/data_aug > runs/exp15/train_1p7b_aug_lr5e5.log 2>&1
genome/exp15/eval.sh 1p7b_aug_lr5e5 mlx-community/Qwen3-1.7B-4bit > runs/exp15/eval_1p7b_aug_lr5e5.log 2>&1
for S in iid para; do
<home>/Documents/GitHub/orbweaver/.venv/bin/python -m genome.exp15.sample --model mlx-community/Qwen3-4B-Instruct-2507-4bit --vocab --max-tokens 200 --set runs/exp15/sets/$S.json --n 4 --out runs/exp15/samples/zs4bi_$S.json
done
echo CHAIN7 DONE
