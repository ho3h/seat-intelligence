#!/bin/zsh
# CPU: score each expected sample file once it exists (one scorer at a time = at most 3 verifier processes)
cd <home>/Genome
TAGS=(1p7b 0p6b 0p6b_lr5e5 4b_lr5e5 1p7b_lr5e5 1p7b_aug_lr5e5 zs4bi)
while true; do
  left=0
  for T in $TAGS; do for S in iid deep para novel; do
    F=runs/exp15/samples/${T}_$S.json
    [ -f runs/exp15/samples/${T}_$S.scored.json ] && continue
    [ $T = zs4bi ] && [ $S = deep -o $S = novel ] && continue
    left=1
    while pgrep -f "genome.exp15.score" > /dev/null; do sleep 5; done
    [ -f runs/exp15/samples/${T}_$S.scored.json ] && continue
    if [ -f $F ]; then python3 -m genome.exp15.score $F >> runs/exp15/score.log 2>&1; fi
  done; done
  [ $left = 0 ] && break
  sleep 20
done
echo SCORE DONE >> runs/exp15/score.log
