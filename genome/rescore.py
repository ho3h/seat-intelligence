"""Re-score saved local_eval outputs with the current extraction (no regeneration)."""
import json, sys, os, collections, re
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
path = sys.argv[1]
d = json.load(open(path)); s = d["summary"]
from genome.verify import verify, verify_b1
from genome import taskset
from genome.corpus import load_all
from genome.g0 import extract_net as _strict
tasks = list(load_all().values()) if s["split"] == "corpus" else taskset.load(s["split"])
def extract_net(t):
    b = _strict(t)
    if b: return b
    m = re.search(r'```[a-zA-Z]*\n(.*)$', t, re.S)
    if m: t = m.group(1)
    lines = t.split('\n'); st = next((i for i, l in enumerate(lines) if re.match(r'^\s*(@\w|def\s)', l)), None)
    if st is None: return None
    body = '\n'.join(lines[st:]).split('```')[0].strip()
    return body + '\n' if body else None
ver = verify if s["arm"] == "native" else verify_b1
def score(kv):
    k, txt = kv; i = int(k.split("_")[0]); net = extract_net(txt)
    if not net: return k, "noblock"
    r = ver(tasks[i], net, seed=0, timeout=4.0, workers=4)
    return k, "pass" if r["status"] == "pass" else ("static" if r["status"] == "reject" else "fail")
with ThreadPoolExecutor(4) as ex: res = dict(ex.map(score, d["raw"].items()))
tot = collections.Counter(res.values()); n = s["n"]
solved = {int(k.split("_")[0]) for k, v in res.items() if v == "pass"}
fam = collections.defaultdict(lambda: [0, 0])
for k, v in res.items():
    t = tasks[int(k.split("_")[0])]; f = t.id.split("_")[1] if t.id.startswith("gen_") else t.tier
    fam[f][0] += v == "pass"; fam[f][1] += 1
out = {"pass@1": tot["pass"] / len(res), f"pass@{n}": len(solved) / len(tasks), "outcomes": dict(tot), "per_family_pass1": {k: round(v[0] / v[1], 3) for k, v in fam.items()}}
print(json.dumps(out)); s.update(out); json.dump(d, open(path, "w"))
