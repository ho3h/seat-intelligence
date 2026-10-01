#!/bin/zsh
# Train-set probe (Theo's request): v1 adapters on 60 of their own training tasks, n=4, same short prompt and sampler.
cd <home>/Genome
PY=<home>/Documents/GitHub/orbweaver/.venv/bin/python
S() { $PY -m genome.exp.sample "$@" 2>&1 | grep --line-buffered -v -i warn; }
Q() { (python3 -m genome.exp.score "$1" > "${1%.json}.metrics.txt" 2>&1 &) }
while [ ! -f runs/exp/phaseC.done ]; do sleep 10; done
S --arm b1 --adapter adapters/bend_v1 --set data/tasksets/train_probe.json --n 4 --batch 120 --max-tokens 900 --seed 3 --out runs/exp/D_bend_v1_train.json; Q runs/exp/D_bend_v1_train.json
S --arm native --adapter adapters/native_v1 --set data/tasksets/train_probe.json --n 4 --batch 120 --max-tokens 900 --seed 3 --out runs/exp/D_native_v1_train.json; Q runs/exp/D_native_v1_train.json
echo done > runs/exp/phaseD.done
