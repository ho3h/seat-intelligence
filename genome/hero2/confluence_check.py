"""Engine self-test: the residual net must not depend on the reduction order (strong confluence). Reduce open call nets and
closed programs under random schedules and compare canonical codes. Dev check on repo nets, not a pair proof."""
import glob, os, random, sys
from genome.hero2 import inet as I
from genome.hero2.prove import call_net

files = sorted(glob.glob("runs/exp3/base/*.native.hvm")) + sorted(glob.glob("runs/exp8/*.hvm")) + sorted(glob.glob("runs/exp10/*.hvm"))[:20]
rng = random.Random(3)
bad = 0; n = 0
for f in files:
    text = open(f).read()
    if "@prog" not in text: continue
    try: reg = I.Registry().add_book(text, "A:").finalize()
    except Exception as e: print("parse fail", f, e); continue
    codes = set()
    for trial in range(4):
        net = call_net("A:")
        eng = I.Engine(reg, rng=random.Random(trial) if trial else None)
        eng.run(net, 200000)
        codes.add(repr(I.canon(net, lambda nm: nm)))
    n += 1
    if len(codes) != 1: bad += 1; print("NONDETERMINISTIC", f)
print("nets", n, "nondeterministic", bad)
