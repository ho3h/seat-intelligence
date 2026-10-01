"""Wiring completion on the plain LM's own nets: for every native_v1 sample the FREE static check rejects (lint), blank its wires, let the
wiring model re-decide them (optionally preferring the LM's own name pairs by a bonus lam), verify. Samples that lint clean are kept
unchanged, so pass@1 is paired sample-for-sample with the baseline and uses no hidden-suite information.

  <venv python> -m genome.exp4.rewire_lm runs/exp/A_native_v1_iid.json --lam 0 --lam 3
"""
import argparse, collections, json, os, sys
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import networkx as nx
from genome.netast import parse_book, print_book
from genome.exp4.skel import _slots, refill
from genome.exp4 import wire as W
from genome.exp4.evalwire import quick_reject
from genome.exp.score import extract, reason_class
from genome.taskgen import task
from genome.verify import verify, check_book


def lenient_skeleton(defs, order):
    sk, names = {}, {}
    for n in order:
        root, reds = defs[n]; acc = []
        r = _slots(root, acc); rs = [(p, _slots(a, acc), _slots(b, acc)) for p, a, b in reds]
        sk[n] = (r, rs); names[n] = acc
    return sk, names


def match(Wm, nm, lam):
    k = len(nm); G = nx.Graph()
    for i in range(k):
        for j in range(i + 1, k): G.add_edge(i, j, weight=float(Wm[i, j]) + (lam if nm[i] == nm[j] else 0.0) + 1e4)
    return sorted(tuple(sorted(p)) for p in nx.max_weight_matching(G, maxcardinality=True))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--lam", type=float, action="append", default=None)
    ap.add_argument("--all", action="store_true", help="re-wire every parseable sample, not only the lint-rejected ones")
    a = ap.parse_args(); lams = a.lam or [0.0]
    raw = json.load(open(a.file)); sc = json.load(open(a.file.replace(".json", ".scored.json")))["scored"]
    progs = {task(f, i).id: task(f, i) for f, i in raw["tasks"]}
    model, V, dev = W.load("runs/exp4/wire.pt", device="cpu")
    for lam in lams:
        out = {pid: [dict(s) for s in v] for pid, v in sc.items()}; jobs = []
        for pid, texts in raw["samples"].items():
            for j, txt in enumerate(texts):
                s = sc[pid][j]
                if s["status"] != "static" and not (a.all and s["status"] in ("pass", "fail")): continue
                net = extract(txt)
                try:
                    defs, order = parse_book(net); sk, nm = lenient_skeleton(defs, order)
                    _, Ws = W.predict_scores(model, V, dev, sk, order)
                    M = {n: match(Ws[n], nm[n], lam) for n in order}
                    jobs.append((pid, j, print_book(refill(sk, order, M, erase_unmatched=True), order)))
                except Exception as e:
                    out[pid][j]["rewire"] = "unparseable"
        def one(job):
            pid, j, book = job
            bad = check_book(book)
            if bad: return pid, j, {"status": "static", "cls": reason_class(bad), "rewire": "still_static"}
            if quick_reject(progs[pid], book): return pid, j, {"status": "fail", "rewire": "fail"}
            r = verify(progs[pid], book, seed=0, timeout=10.0, workers=4)
            return pid, j, {"status": r["status"] if r["status"] != "reject" else "static", "rewire": r["status"], "net": book}
        with ThreadPoolExecutor(6) as ex:
            for pid, j, r in ex.map(one, jobs): out[pid][j] = r
        sp = a.file.replace(".json", f".rewire{'all' if a.all else ''}_lam{lam:g}.scored.json")
        json.dump({"meta": raw["meta"], "tasks": raw["tasks"], "scored": out}, open(sp, "w"))
        from genome.exp.metrics import summarize, paired
        s = summarize(sp)
        rc = collections.Counter(x.get("rewire") for v in out.values() for x in v if "rewire" in x)
        print(f"lam={lam}: rewired {len(jobs)} static samples -> {dict(rc)}")
        print(json.dumps({k: s[k] for k in ("pass@1", "pass@1_task_boot95", "static_filter_best_of_8", "static_clean_rate", "per_family_pass@1") if k in s}))
        print("paired vs baseline:", paired(a.file.replace(".json", ".scored.json"), sp), flush=True)


if __name__ == "__main__": main()
