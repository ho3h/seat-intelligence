"""Verify every sample of a genome.exp.sample file (CPU). Per sample: noblock | static | fail | pass, with the static reason class.

  python3 -m genome.exp.score runs/exp/x.json            -> writes runs/exp/x.scored.json and prints metrics
Extraction is the same lenient rule as genome.local_eval (strict fenced block, else unclosed fence / first definition line).
Verification is genome.verify.verify / verify_b1 at seed 0 (unchanged semantics); timeout 10 s per case.
"""
import json, os, re, sys, collections
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from genome.verify import verify, verify_b1
from genome.taskgen import task
from genome.g0 import extract_net as _strict


def extract(t):
    b = _strict(t)
    if b: return b
    m = re.search(r'```[a-zA-Z]*\n(.*)$', t, re.S)
    if m: t = m.group(1)
    lines = t.split('\n'); st = next((i for i, l in enumerate(lines) if re.match(r'^\s*(@\w|def\s)', l)), None)
    if st is None: return None
    body = '\n'.join(lines[st:]).split('```')[0].strip()
    return body + '\n' if body else None


def reason_class(reason):
    r = reason or ""
    if "appears only once" in r: return "wire_once"
    if re.search(r"appears \d+ times", r): return "wire_many"
    if "brackets do not balance" in r: return "brackets"
    if "is not defined" in r: return "undef_ref"
    if "did not compile" in r: return "bend_compile"
    return "other_static"


def score_file(path, workers=6):
    d = json.load(open(path)); arm = d["meta"]["arm"]; ver = verify if arm == "native" else verify_b1
    progs = {task(f, i).id: task(f, i) for f, i in d["tasks"]}
    jobs = [(pid, j, txt) for pid, texts in d["samples"].items() for j, txt in enumerate(texts)]
    def one(job):
        pid, j, txt = job; net = extract(txt)
        if not net: return pid, j, {"status": "noblock"}
        try: r = ver(progs[pid], net, seed=0, timeout=10.0, workers=4)
        except Exception as e: return pid, j, {"status": "fail", "why": f"harness error {e!r}"[:200]}
        if r["status"] == "pass": return pid, j, {"status": "pass", "net": net, "itrs": r["metrics"].get("itrs_median_big")}
        if r["status"] == "reject": return pid, j, {"status": "static", "cls": reason_class(r["reason"]), "why": r["reason"][:300]}
        return pid, j, {"status": "fail", "why": r["counterexample"]["why"][:120]}
    res = collections.defaultdict(dict)
    with ThreadPoolExecutor(workers) as ex:
        for pid, j, r in ex.map(one, jobs): res[pid][j] = r
    out = {pid: [res[pid][j] for j in range(len(d["samples"][pid]))] for pid in d["samples"]}
    sp = path.replace(".json", ".scored.json")
    json.dump({"meta": d["meta"], "tasks": d["tasks"], "scored": out}, open(sp, "w"))
    return sp


if __name__ == "__main__":
    from genome.exp.metrics import summarize
    for p in sys.argv[1:]:
        sp = score_file(p); print(p); print(json.dumps(summarize(sp), indent=1))
