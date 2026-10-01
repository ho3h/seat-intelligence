"""Map taskgen pipeline stage descriptions onto the exp6 DSL catalog and check semantics on random inputs."""
import random, re
from genome.taskgen import fam_pipeline
from genome.exp6.synth import CAT, py_run

def desc2name(d):
    pats = [(r"keep only the elements x for which x > (\d+)$", "gt{}"), (r"keep only the elements x for which x < (\d+)$", "lt{}"),
            (r"keep only the elements x for which x >= (\d+)$", "ge{}"), (r"x is even$", "mod2eq0"), (r"x is odd$", "mod2eq1"),
            (r"x mod (\d+) equals (\d+)$", "mod{}eq{}"), (r"by x\*(\d+)\+(\d+) \(mod", "aff{}_{}"), (r"by x xor (\d+)$", "xor{}"),
            (r"by x and (\d+)$", "and{}"), (r"by x\+(\d+) \(mod", "add{}"), (r"by x\*x", "sq"), (r"by x mod (\d+)$", "mod{}"),
            (r"integer-divided by (\d+)$", "div{}"), (r"keep only the first (\d+)", "take{}"), (r"remove the first (\d+)", "drop{}"),
            (r"reverse the order", "rev"), (r"collapse every run", "dedup"), (r"running totals", "scan"), (r"sort ascending", "sort")]
    for p, n in pats:
        m = re.search(p, d)
        if m: return n.format(*m.groups())
    return None

def main(n=2000):
    rng = random.Random(0); cov = 0; bad = 0; lens = {}
    for i in range(n):
        t = fam_pipeline(i); names = [desc2name(d) for d, _ in t.steps]
        ok = all(x in CAT for x in names)
        if ok:
            for _ in range(20):
                xs = [rng.randrange(1000) for _ in range(rng.randint(0, 16))]
                if py_run(names, xs) != t.ref(xs): ok = False; bad += 1; break
        cov += ok; lens[len(names)] = lens.get(len(names), 0) + 1
    print(f"pipeline tasks {n}: expressible+semantics-checked {cov}, semantic mismatches {bad}, stage-count histogram {lens}")

main()
