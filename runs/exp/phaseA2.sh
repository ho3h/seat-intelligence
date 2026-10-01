#!/bin/zsh
# Phase A (continued, larger batches, max 900 new tokens as in the original local_eval). Waits for the native iid run already in flight.
cd <home>/Genome
PY=<home>/Documents/GitHub/orbweaver/.venv/bin/python
S() { $PY -m genome.exp.sample "$@" 2>&1 | grep --line-buffered -v -i warn; }
Q() { (python3 -m genome.exp.score "$1" > "${1%.json}.metrics.txt" 2>&1 &) }
while [ ! -f runs/exp/A_native_v1_iid.json ]; do sleep 5; done; Q runs/exp/A_native_v1_iid.json
S --arm b1 --adapter adapters/bend_v1 --set data/tasksets/iid_test.json --n 8 --batch 120 --max-tokens 900 --out runs/exp/A_bend_v1_iid.json; Q runs/exp/A_bend_v1_iid.json
S --arm native --adapter adapters/native_v1 --set data/tasksets/ei_pool.json --n 4 --seed 1 --batch 128 --max-tokens 900 --out runs/exp/A_native_v1_pool.json; Q runs/exp/A_native_v1_pool.json
S --arm b1 --adapter adapters/bend_v1 --set data/tasksets/ei_pool.json --n 4 --seed 1 --batch 128 --max-tokens 900 --out runs/exp/A_bend_v1_pool.json; Q runs/exp/A_bend_v1_pool.json
echo done > runs/exp/phaseA.done
S --arm b1 --primer --set data/tasksets/iid_test.json --n 2 --batch 60 --max-tokens 900 --out runs/exp/A_bend_base_primer_iid.json; Q runs/exp/A_bend_base_primer_iid.json
echo done > runs/exp/phaseA2.done
