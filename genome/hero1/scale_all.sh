#!/bin/zsh
# scale test: policies P1 and P2 on 1k/10k/100k synthetic guests; native (wall clock, 3 repeats), depth oracle, rust decode-check at 1k
cd "$(dirname "$0")/../.."
rm -f runs/hero1/scale.jsonl
for P in P1 P2; do
  python3 -m genome.hero1.scale rust $P 1000 > /dev/null
  python3 -m genome.hero1.scale full $P 1000 10000 > /dev/null
  for i in 1 2 3; do python3 -m genome.hero1.scale native $P 1000 10000 100000 > /dev/null; done
  python3 -m genome.hero1.scale depth $P 1000 10000 100000 > /dev/null
done
echo scale done
