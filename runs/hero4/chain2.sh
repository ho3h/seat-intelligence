#!/bin/zsh
# HERO-4 evaluation chain 1: main model (alias-tuned 1.7B) arms, then ablation + retrain trainings and their evals, then zero-shot 4B.
cd /Users/tedsandtads/Genome
PY=/Users/tedsandtads/Documents/GitHub/orbweaver/.venv/bin/python
M=mlx-community/Qwen3-1.7B-4bit
TEST=runs/hero4/sets/FROZEN/test_final.json; IID=runs/hero4/sets/FROZEN/iid_base.json
NEWF=limit,pair,apart,vip,stagger,headseat,bigfirst,waitlist,snake,sectionlead
S(){ $PY -m genome.hero4.sample "$@"; }
S --model $M --adapter adapters/hero4_main --set $TEST --arm all --n 4 --batch 16 --out runs/hero4/samples/main_all.json
S --model $M --adapter adapters/hero4_main --set $IID --arm all --n 4 --batch 16 --out runs/hero4/samples/main_iid_all.json
echo MAIN-SAMPLED
python3 -m genome.hero4.score runs/hero4/samples/main_without.json runs/hero4/samples/main_own.json runs/hero4/samples/main_all.json runs/hero4/samples/main_iid_without.json runs/hero4/samples/main_iid_all.json > runs/hero4/score_main.log 2>&1 &
# ablation: constant names
genome/hero4/train.sh const $M 600 5e-5 runs/hero4/data_const > runs/hero4/train_const.log 2>&1
S --model $M --adapter adapters/hero4_const --set $TEST --arm own --only $NEWF --n 4 --batch 16 --out runs/hero4/samples/const_own.json
S --model $M --adapter adapters/hero4_const --set $TEST --arm without --only group,spread,order,sections,captains --n 4 --batch 16 --out runs/hero4/samples/const_without.json
echo CONST-SAMPLED
python3 -m genome.hero4.score runs/hero4/samples/const_own.json runs/hero4/samples/const_without.json > runs/hero4/score_const.log 2>&1 &
# control: retrain with the ten new words
genome/hero4/train.sh retrain $M 600 5e-5 runs/hero4/data_retrain > runs/hero4/train_retrain.log 2>&1
S --model $M --adapter adapters/hero4_retrain --set $TEST --arm all --n 4 --batch 16 --out runs/hero4/samples/retrain_all.json
echo RETRAIN-SAMPLED
python3 -m genome.hero4.score runs/hero4/samples/retrain_all.json > runs/hero4/score_retrain.log 2>&1 &
# control: untuned 4B instruct, all 15 words in the prompt
S --model mlx-community/Qwen3-4B-Instruct-2507-4bit --set $TEST --arm all --n 4 --max-tokens 160 --out runs/hero4/samples/zs4b_all.json
python3 -m genome.hero4.score runs/hero4/samples/zs4b_all.json > runs/hero4/score_zs4b.log 2>&1
echo CHAIN1-DONE
