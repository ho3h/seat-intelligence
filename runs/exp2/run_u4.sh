#!/bin/zsh
# Same-loop unconstrained control, n=4 (time box), otherwise identical settings.
cd <home>/Genome
PY=<home>/Documents/GitHub/orbweaver/.venv/bin/python
$PY -m genome.exp2.csample --adapter adapters/native_v1 --set data/tasksets/iid_test.json --n 4 --off --out runs/exp2/U_native_v1_iid.json 2>&1 | grep --line-buffered -v -i warn
python3 -m genome.exp.score runs/exp2/U_native_v1_iid.json > runs/exp2/U_native_v1_iid.metrics.txt 2>&1
echo done > runs/exp2/run.done
