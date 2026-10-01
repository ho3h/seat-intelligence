#!/bin/zsh
# zero-shot control (no fine-tune): Qwen3-4B-Instruct-2507 with the vocabulary documented in the prompt
cd /Users/tedsandtads/Genome
until grep -q "CHAIN3 DONE" runs/exp15/chain3.log; do sleep 20; done
for S in iid para; do
/Users/tedsandtads/Documents/GitHub/orbweaver/.venv/bin/python -m genome.exp15.sample --model mlx-community/Qwen3-4B-Instruct-2507-4bit --vocab --max-tokens 200 --set runs/exp15/sets/$S.json --n 4 --out runs/exp15/samples/zs4bi_$S.json
done
echo CHAIN4 DONE
