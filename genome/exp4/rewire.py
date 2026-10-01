"""Oracle-skeleton check on the step-2 test set: take the baseline's (native_v1) PASSING nets on iid_test, blank their wires, re-wire
with the wiring model, verify. Measures the matcher on correct skeletons of the exact step-2 tasks (in the LM's own style).

  <venv python> -m genome.exp4.rewire runs/exp/A_native_v1_iid.scored.json
"""
import json, os, sys, collections
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); os.chdir(ROOT)
from genome.netast import parse_book, print_book
from genome.exp4.skel import to_skeleton, refill
from genome.exp4 import wire as W
from genome.exp4.evalwire import quick_reject
from genome.taskgen import task
from genome.verify import verify


def main():
    d = json.load(open(sys.argv[1])); progs = {task(f, i).id: task(f, i) for f, i in d["tasks"]}
    model, V, dev = W.load("runs/exp4/wire.pt", device="cpu")
    jobs = []
    for pid, v in d["scored"].items():
        for s in v:
            if s["status"] == "pass":
                defs, order = parse_book(s["net"]); sk, gold = to_skeleton(defs, order)
                M = W.predict(model, V, dev, sk, order)
                jobs.append((pid, all(M[n] == gold[n] for n in order), print_book(refill(sk, order, M), order)))
    def one(j):
        pid, exact, book = j
        if exact: return pid, "pass_exact"
        if quick_reject(progs[pid], book): return pid, "fail"
        return pid, verify(progs[pid], book, seed=0, timeout=10.0, workers=4)["status"]
    with ThreadPoolExecutor(6) as ex: res = list(ex.map(one, jobs))
    c = collections.Counter(r for _, r in res)
    fam = collections.defaultdict(lambda: [0, 0])
    for pid, r in res: f = pid[4:].rsplit("_", 1)[0]; fam[f][0] += r.startswith("pass"); fam[f][1] += 1
    out = {"nets": len(res), "outcomes": dict(c), "exec_pass": round(sum(r.startswith("pass") for _, r in res) / len(res), 4), "by_family": dict(fam),
           "tasks_with_a_rewired_pass": len({p for p, r in res if r.startswith("pass")}), "tasks": len({p for p, _ in res})}
    print(json.dumps(out, indent=1)); json.dump(out, open("runs/exp4/rewire_native_v1_passes.json", "w"), indent=1)


if __name__ == "__main__": main()
