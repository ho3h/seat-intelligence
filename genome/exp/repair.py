"""Mechanical lint repair (no model): in each definition, a wire that appears exactly once is replaced by an eraser `*`.
The verifier decides whether the repaired net is right; nothing else changes. Measures how much of the static failure
mass is 'forgot to erase an unused value'.

  python3 -m genome.exp.repair runs/exp/A_native_v1_iid.scored.json   -> writes *.repaired.json, prints metrics
"""
import json, re, sys, os, collections
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
from genome.netast import tokens
from genome.verify import verify, lint_net
from genome.taskgen import task
from genome.exp.score import extract


def erase_singletons(book):
    text = re.sub(r"//[^\n]*", "", book)
    parts = re.split(r"(?m)^\s*(?=@[\w/]+\s*=)", text); out = []
    for blk in parts:
        m = re.match(r"\s*@([\w/]+)\s*=", blk)
        if not m: out.append(blk); continue
        body = blk[m.end():]
        cnt = collections.Counter(t for t in tokens(body) if re.fullmatch(r"[A-Za-z_]\w*", t))
        for v, c in cnt.items():
            if c == 1: body = re.sub(rf"(?<![\w@\[]){re.escape(v)}(?![\w\]])", "*", body, count=1)
        out.append(blk[:m.end()] + body)
    return "\n".join(x.rstrip() for x in out) + "\n"


def main(scored):
    d = json.load(open(scored)); S = d["scored"]
    raw = json.load(open(scored.replace(".scored.json", ".json")))["samples"]
    progs = {task(f, i).id: task(f, i) for f, i in d["tasks"]}
    jobs = [(pid, j) for pid, v in S.items() for j, s in enumerate(v) if s["status"] == "static" and s.get("cls") == "wire_once"]
    def one(job):
        pid, j = job; net = extract(raw[pid][j]); fixed = erase_singletons(net)
        if lint_net(fixed): return pid, j, "static"
        return pid, j, verify(progs[pid], fixed, seed=0, timeout=10.0, workers=4)["status"]
    with ThreadPoolExecutor(6) as ex: res = list(ex.map(one, jobs))
    new = {pid: [dict(s) for s in v] for pid, v in S.items()}
    for pid, j, st in res: new[pid][j] = {"status": st if st != "reject" else "static", "cls": "after_repair"}
    out = scored.replace(".scored.json", ".repaired.scored.json")
    json.dump({"meta": d["meta"], "tasks": d["tasks"], "scored": new}, open(out, "w"))
    from genome.exp.metrics import summarize
    print(json.dumps({"repaired_candidates": len(jobs), "after": collections.Counter(r[2] for r in res)}))
    print(json.dumps(summarize(out), indent=1))


if __name__ == "__main__": main(sys.argv[1])
