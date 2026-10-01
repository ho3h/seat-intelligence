#!/bin/sh
# verify every net in runs/exp10 on seeds 0 1 2 (3 worker processes)
cd <home>/Genome
for f in runs/exp10/t5_*.hvm; do p=$(basename $f .hvm); python3 runs/exp10/v.py $p $f 0 1 2; done
