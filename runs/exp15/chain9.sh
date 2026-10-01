#!/bin/zsh
# 4B lr5e-5 600-iter run was killed externally at iter ~250 (no error in log). Rerun at 300 iters to fit the time box.
cd /Users/tedsandtads/Genome
while pgrep -f "python.* -m mlx_lm lora" > /dev/null; do sleep 10; done
genome/exp15/eval.sh 1p7b_lr5e5 mlx-community/Qwen3-1.7B-4bit > runs/exp15/eval_1p7b_lr5e5.log 2>&1
genome/exp15/train.sh 4b_lr5e5 mlx-community/Qwen3-4B-4bit 300 5e-5 > runs/exp15/train_4b_lr5e5.log 2>&1
genome/exp15/eval.sh 4b_lr5e5 mlx-community/Qwen3-4B-4bit > runs/exp15/eval_4b_lr5e5.log 2>&1
for S in iid para; do
/Users/tedsandtads/Documents/GitHub/orbweaver/.venv/bin/python -m genome.exp15.sample --model mlx-community/Qwen3-4B-Instruct-2507-4bit --vocab --max-tokens 200 --set runs/exp15/sets/$S.json --n 4 --out runs/exp15/samples/zs4bi_$S.json
done
echo CHAIN9 DONE
