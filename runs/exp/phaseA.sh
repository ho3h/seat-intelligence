#!/bin/zsh
# Phase A: baselines on the fair iid test (n=8) + expert-iteration pool sampling (n=4). One GPU job at a time; scoring overlaps.
cd /Users/tedsandtads/Genome
PY=/Users/tedsandtads/Documents/GitHub/orbweaver/.venv/bin/python
S() { $PY -m genome.exp.sample "$@" 2>&1 | grep -v -i warn; }
Q() { (python3 -m genome.exp.score "$1" > "${1%.json}.metrics.txt" 2>&1 &) }
S --arm native --adapter adapters/native_v1 --set data/tasksets/iid_test.json --n 8 --out runs/exp/A_native_v1_iid.json; Q runs/exp/A_native_v1_iid.json
S --arm b1 --adapter adapters/bend_v1 --set data/tasksets/iid_test.json --n 8 --out runs/exp/A_bend_v1_iid.json; Q runs/exp/A_bend_v1_iid.json
S --arm b1 --primer --set data/tasksets/iid_test.json --n 2 --batch 16 --out runs/exp/A_bend_base_primer_iid.json; Q runs/exp/A_bend_base_primer_iid.json
S --arm native --adapter adapters/native_v1 --set data/tasksets/ei_pool.json --n 4 --seed 1 --out runs/exp/A_native_v1_pool.json; Q runs/exp/A_native_v1_pool.json
S --arm b1 --adapter adapters/bend_v1 --set data/tasksets/ei_pool.json --n 4 --seed 1 --out runs/exp/A_bend_v1_pool.json; Q runs/exp/A_bend_v1_pool.json
echo done > runs/exp/phaseA.done
