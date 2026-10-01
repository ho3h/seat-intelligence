"""Fresh-seed audit: re-verify a random sample of passing (task, program) pairs at seed 1 (the pass verdicts used seed 0).
   python3 -m genome.exp15.audit runs/exp15/samples/1p7b_iid.scored.json runs/exp15/samples/1p7b_deep.scored.json
"""
import json, random, sys
from concurrent.futures import ThreadPoolExecutor
from genome.verify import verify
from genome.exp15.lang import parse, assemble
from genome.exp15.data import load_task

pairs = []
for f in sys.argv[1:]:
    d = json.load(open(f))
    for pid, v in d["scored"].items():
        for s in v:
            if s["status"] == "pass": pairs.append((f, pid, s["prog"])); break
random.Random(0).shuffle(pairs); pairs = pairs[:40]
specs = {}
for f in sys.argv[1:]:
    for s in json.load(open(f))["specs"]: specs[load_task(s).id] = s
def one(x):
    f, pid, prog = x; p = load_task(specs[pid]); st, rd = parse(prog)
    return pid, verify(p, assemble(st, rd), seed=1, timeout=10.0, workers=1)["status"]
with ThreadPoolExecutor(3) as ex: res = list(ex.map(one, pairs))
ok = sum(r == "pass" for _, r in res)
out = {"audited": len(res), "pass_seed1": ok, "failures": [x for x in res if x[1] != "pass"]}
json.dump(out, open("runs/exp15/audit_seed1.json", "w"), indent=1); print(out)
