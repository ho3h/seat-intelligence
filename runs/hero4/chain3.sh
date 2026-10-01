#!/bin/zsh
# round 2 + replicate evaluation on the fresh frozen sets (FROZEN2): test v2 (new families) and base test v2
cd <home>/Genome
PY=<home>/Documents/GitHub/orbweaver/.venv/bin/python
M=mlx-community/Qwen3-1.7B-4bit; A=adapters/hero4_main
F2=runs/hero4/sets/FROZEN2; E2=runs/hero4/entries_v2_FROZEN.json
S(){ $PY -m genome.hero4.sample --model $M --adapter $A --n 4 --batch 16 "$@"; }
S --set $F2/testv2_final.json --arm own --out runs/hero4/samples/tv2_r1_own.json
HERO4_ENTRIES_FILE=$E2 S --set $F2/testv2_final.json --arm own --out runs/hero4/samples/tv2_r2_own.json
S --set $F2/btv2_final.json --arm without --out runs/hero4/samples/btv2_without.json
HERO4_ENTRIES_FILE=$E2 S --set $F2/btv2_final.json --arm all --out runs/hero4/samples/btv2_r2_all.json
HERO4_ENTRIES_FILE=$E2 S --set $F2/btv2_final.json --arm one --out runs/hero4/samples/btv2_r2_one.json
S --set $F2/btv2_final.json --arm all --out runs/hero4/samples/btv2_r1_all.json
S --set $F2/btv2_final.json --arm one --out runs/hero4/samples/btv2_r1_one.json
HERO4_ENTRIES_FILE=$E2 S --set $F2/testv2_final.json --arm all --out runs/hero4/samples/tv2_r2_all.json
S --set $F2/testv2_final.json --arm all --out runs/hero4/samples/tv2_r1_all.json
S --set $F2/testv2_final.json --arm without --out runs/hero4/samples/tv2_without.json
echo CHAIN3-SAMPLED
python3 -m genome.hero4.score runs/hero4/samples/tv2_r1_own.json runs/hero4/samples/tv2_r2_own.json runs/hero4/samples/btv2_without.json runs/hero4/samples/btv2_r2_all.json runs/hero4/samples/btv2_r2_one.json runs/hero4/samples/btv2_r1_all.json runs/hero4/samples/btv2_r1_one.json runs/hero4/samples/tv2_r2_all.json runs/hero4/samples/tv2_r1_all.json runs/hero4/samples/tv2_without.json > runs/hero4/score_chain3.log 2>&1
echo CHAIN3-DONE
