#!/bin/zsh
# Greedy decoding (temp 0, one sample) for the v1 adapters on the iid test: is temp 0.7 costing pass@1?
cd /Users/tedsandtads/Genome
PY=/Users/tedsandtads/Documents/GitHub/orbweaver/.venv/bin/python
S() { $PY -m genome.exp.sample "$@" 2>&1 | grep --line-buffered -v -i warn; }
Q() { (python3 -m genome.exp.score "$1" > "${1%.json}.metrics.txt" 2>&1 &) }
while [ ! -f runs/exp/phaseD.done ]; do sleep 10; done
S --arm b1 --adapter adapters/bend_v1 --set data/tasksets/iid_test.json --n 1 --temp 0 --batch 120 --max-tokens 900 --out runs/exp/E_bend_v1_iid_greedy.json; Q runs/exp/E_bend_v1_iid_greedy.json
S --arm native --adapter adapters/native_v1 --set data/tasksets/iid_test.json --n 1 --temp 0 --batch 120 --max-tokens 900 --out runs/exp/E_native_v1_iid_greedy.json; Q runs/exp/E_native_v1_iid_greedy.json
echo done > runs/exp/phaseE.done
