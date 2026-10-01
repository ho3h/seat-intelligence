"""Freeze the benchmark labels BEFORE the tester/rewriter run: python-only evidence for each label, code hashes."""
import hashlib, itertools, json, random, time
from . import folds as F

def h(path): return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]

def evidence(f, n=8000, seed=99):
    """Python-only label evidence on the tree-reachable state domain: the closure of {unit} + lift(x) under comb."""
    rng = random.Random(seed)
    pool = {f.unit} | {f.py_lift(x) for x in f.enum} | {f.py_lift(f.gen(rng)) for _ in range(250)}
    for _ in range(3):
        cur = list(pool)
        for _ in range(900): pool.add(f.py_comb(rng.choice(cur), rng.choice(cur)))
    for l in [list(c) for k in range(0, 4) for c in itertools.product(f.enum, repeat=k)]: pool.add(f.state_of(l))
    pool = list(pool)
    wit = None; comm_bad = 0; idl = idr = 0
    for _ in range(n):
        a, b, c = (rng.choice(pool) for _ in range(3))
        if wit is None and f.py_comb(f.py_comb(a, b), c) != f.py_comb(a, f.py_comb(b, c)): wit = (a, b, c)
        if f.py_comb(a, b) != f.py_comb(b, a): comm_bad += 1
    for a in pool:
        idl += f.py_comb(f.unit, a) != a; idr += f.py_comb(a, f.unit) != a
    return dict(pool=len(pool), assoc_witness=wit, python_comm_violations=comm_bad, python_idl_fail=idl, python_idr_fail=idr)

rows = {}
for f in F.FOLDS:
    ev = evidence(f)
    ok = True
    if f.label == "assoc": ok = ev["assoc_witness"] is None and ev["python_idl_fail"] == 0 and ev["python_idr_fail"] == 0 and (f.comm == (ev["python_comm_violations"] == 0))
    if f.label == "nonassoc": ok = ev["assoc_witness"] is not None or ev["python_idl_fail"] > 0 or ev["python_idr_fail"] > 0
    rows[f.id] = dict(label=f.label, comm=f.comm, corpus=f.corpus, flavour=f.flavour, evidence=ev, label_consistent=ok)
    print(f"{f.id:24s} {f.label:11s} consistent={ok} witness={ev['assoc_witness']} commviol={ev['python_comm_violations']} idfail={ev['python_idl_fail']},{ev['python_idr_fail']}")
out = dict(frozen_at=time.strftime("%Y-%m-%d %H:%M:%S"), n_assoc=len(F.assoc()), n_nonassoc=len(F.nonassoc()), n_adversarial=len(F.adversarial()),
           hashes={p: h(p) for p in ["genome/hero3/folds.py", "genome/hero3/tester.py", "genome/hero3/nets.py", "genome/hero3/netbuild.py", "genome/hero3/programs.py"]},
           folds=rows)
json.dump(out, open("runs/hero3/PREREG.json", "w"), indent=1, default=str)
print(out["hashes"])
