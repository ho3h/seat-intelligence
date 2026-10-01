"""Check the HVM4 interpreter against the Python stage semantics (all 108 stages + random 3-stage programs)."""
import random, re, sys
from genome.exp6.synth import *

def main():
    rng = random.Random(0)
    names = list(CAT)
    progs = [[n] for n in names] + [[rng.choice(names) for _ in range(rng.randint(2, 3))] for _ in range(300)]
    inputs = [[rng.randrange(hi) for _ in range(rng.randint(0, 12))] for hi in (10, 30, 100, 1000) for _ in range(2)] + [[16777215, 5, 5, 0]]
    bad = 0; tot = 0
    for xs in inputs:
        terms = ",".join(f"@exec({hlist([CAT[n][0] for n in p])}, {hlist(xs)})" for p in progs)
        src = INTERP + f"\n@main = [{terms}]\n"
        open("runs/exp6/validate.hvm", "w").write(src)
        out = subprocess.run([HVM, "runs/exp6/validate.hvm"], capture_output=True, text=True).stdout.strip()
        got = eval(ANSI.sub("", out))
        for p, g in zip(progs, got):
            tot += 1
            if g != py_run(p, xs): bad += 1; print("MISMATCH", p, xs, g, py_run(p, xs))
    print(f"validated {tot} (program,input) pairs, mismatches {bad}")

main()
