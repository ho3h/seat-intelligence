#!/bin/sh
# build + verify one program: runs/exp5/v.sh <prog> [K]
cd /Users/tedsandtads/Genome && python3 runs/exp5/build.py "$@" && python3 -m genome.verify $1 runs/exp5/$1.hvm --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status'), d.get('metrics'), d.get('counterexample') or '', d.get('reason') or '')"
