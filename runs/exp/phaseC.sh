#!/bin/zsh
# Replaces phaseA2 (tail) + phaseB after a time re-plan: GPU jobs strictly sequential, CPU scoring overlapped.
# 1 score native pool (bg) || Bend pool sampling n=2   2 native EI train + eval (n=4)   3 Bend EI train + eval (n=4)
# 4 native control (same iters, original data) + eval (n=4). Base-primer Bend calibration run dropped for time.
cd <home>/Genome
PY=<home>/Documents/GitHub/orbweaver/.venv/bin/python
M=mlx-community/Qwen3-4B-Instruct-2507-4bit
T() { $PY -m mlx_lm lora --model $M --train --batch-size 4 --num-layers 16 --learning-rate 1e-4 --mask-prompt --max-seq-length 2048 \
      --steps-per-eval 50 --save-every 1000 --seed 0 "$@" 2>&1 | grep --line-buffered -E "Val loss|Train loss|Saved final" ; }
S() { $PY -m genome.exp.sample "$@" 2>&1 | grep --line-buffered -v -i warn; }
Q() { (python3 -m genome.exp.score "$1" > "${1%.json}.metrics.txt" 2>&1 &) }
W() { until grep -q per_family "${1%.json}.metrics.txt" 2>/dev/null; do sleep 10; done; }
while [ ! -f runs/exp/A_native_v1_pool.json ] || pgrep -f "genome.exp.sample" > /dev/null; do sleep 5; done
Q runs/exp/A_native_v1_pool.json
S --arm b1 --adapter adapters/bend_v1 --set data/tasksets/ei_pool.json --n 2 --seed 1 --batch 128 --max-tokens 900 --out runs/exp/A_bend_v1_pool.json; Q runs/exp/A_bend_v1_pool.json
W runs/exp/A_native_v1_pool.json
python3 -m genome.exp.build_ei native runs/exp/A_native_v1_pool.scored.json data/sft_ei_native > runs/exp/ei_native.txt
IN=$(python3 -c "import json;print(json.load(open('runs/exp/ei_native.txt'))['iters'])")
T --data data/sft_ei_native --adapter-path adapters/native_ei1 --resume-adapter-file adapters/native_v1/adapters.safetensors --iters $IN > runs/exp/train_native_ei1.log
S --arm native --adapter adapters/native_ei1 --set data/tasksets/iid_test.json --n 4 --batch 120 --max-tokens 900 --seed 2 --out runs/exp/B_native_ei1_iid.json; Q runs/exp/B_native_ei1_iid.json
W runs/exp/A_bend_v1_pool.json
python3 -m genome.exp.build_ei b1 runs/exp/A_bend_v1_pool.scored.json data/sft_ei_b1 > runs/exp/ei_b1.txt
IB=$(python3 -c "import json;print(json.load(open('runs/exp/ei_b1.txt'))['iters'])")
T --data data/sft_ei_b1 --adapter-path adapters/bend_ei1 --resume-adapter-file adapters/bend_v1/adapters.safetensors --iters $IB > runs/exp/train_bend_ei1.log
S --arm b1 --adapter adapters/bend_ei1 --set data/tasksets/iid_test.json --n 4 --batch 120 --max-tokens 900 --seed 2 --out runs/exp/B_bend_ei1_iid.json; Q runs/exp/B_bend_ei1_iid.json
T --data data/sft --adapter-path adapters/native_ctrl1 --resume-adapter-file adapters/native_v1/adapters.safetensors --iters $IN > runs/exp/train_native_ctrl1.log
S --arm native --adapter adapters/native_ctrl1 --set data/tasksets/iid_test.json --n 4 --batch 120 --max-tokens 900 --seed 2 --out runs/exp/B_native_ctrl1_iid.json; Q runs/exp/B_native_ctrl1_iid.json
echo done > runs/exp/phaseC.done
