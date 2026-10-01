#!/bin/zsh
cd <home>/Genome
until grep -q "CHAIN2 DONE" runs/exp15/chain2.log; do sleep 20; done
<home>/Documents/GitHub/orbweaver/.venv/bin/python -m genome.exp15.sample --model mlx-community/Qwen3-1.7B-4bit --adapter adapters/exp15_1p7b --set runs/exp15/sets/novel.json --n 4 --out runs/exp15/samples/1p7b_novel.json
echo CHAIN3 DONE
