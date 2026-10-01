#!/bin/zsh
# Constrained decoding vs same-loop unconstrained control, native_v1 on iid_test (n=8, temp 0.7, top_p 0.95, max 1200, batch 48).
cd <home>/Genome
PY=<home>/Documents/GitHub/orbweaver/.venv/bin/python
$PY -m genome.exp2.csample --adapter adapters/native_v1 --set data/tasksets/iid_test.json --n 8 --out runs/exp2/C_native_v1_iid.json 2>&1 | grep --line-buffered -v -i warn
(python3 -m genome.exp.score runs/exp2/C_native_v1_iid.json > runs/exp2/C_native_v1_iid.metrics.txt 2>&1 &)
$PY -m genome.exp2.csample --adapter adapters/native_v1 --set data/tasksets/iid_test.json --n 8 --off --out runs/exp2/U_native_v1_iid.json 2>&1 | grep --line-buffered -v -i warn
python3 -m genome.exp.score runs/exp2/U_native_v1_iid.json > runs/exp2/U_native_v1_iid.metrics.txt 2>&1
echo done > runs/exp2/run.done
