"""Invariance check: a net and a purely syntactic scramble of it (renamed wires, renamed definitions, shuffled statements, redex sides
swapped, definitions reordered) must be proved equal at tier S. Tests that the canonical form does not depend on names or order."""
import glob, os, random, sys
from genome.netast import parse_book, print_book
from genome.hero2.prove import Prover


def ren_tree(t, vm, dm):
    k = t[0]
    if k == "var": return ("var", vm.setdefault(t[1], f"w{len(vm)}_{random.randrange(10**6)}"))
    if k == "ref": return ("ref", dm.get(t[1], t[1]))
    if k in ("con", "dup", "opr", "swi"): return (k, ren_tree(t[1], vm, dm), ren_tree(t[2], vm, dm))
    return t


def scramble(text, rng):
    defs, order = parse_book(text)
    dm = {n: (n if n == "prog" else f"d{rng.randrange(10**6)}_{i}") for i, n in enumerate(order)}
    new = {}
    for n in order:
        root, reds = defs[n]; vm = {}
        r2 = ren_tree(root, vm, dm)
        rs = []
        for par, a, b in reds:
            a2, b2 = ren_tree(a, vm, dm), ren_tree(b, vm, dm)
            rs.append((par, b2, a2) if rng.random() < .5 else (par, a2, b2))
        rng.shuffle(rs)
        new[dm[n]] = (r2, rs)
    o2 = [dm[n] for n in order]; rng.shuffle(o2)
    return print_book(new, o2)


rng = random.Random(5)
files = sorted(glob.glob("runs/exp3/base/*.native.hvm")) + sorted(glob.glob("runs/exp8/*.hvm"))
bad = []
for f in files:
    text = open(f).read()
    if "@prog" not in text: continue
    v = Prover(text, scramble(text, rng)).prove()
    if not (v.equal and v.tier == "S"): bad.append((os.path.basename(f), v.tier, v.reason))
print(f"scrambled copies proved equal at tier S: {len([f for f in files if '@prog' in open(f).read()]) - len(bad)}/{len([f for f in files if '@prog' in open(f).read()])}; failures: {bad[:5]}")
