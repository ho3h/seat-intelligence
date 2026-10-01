"""Stage 1: trace every problem of a frozen set (both policies), and time the untraced baselines.
usage: python3 -m genome.hero5.trace_all <set.json> <outdir> [workers]"""
import sys, os, json, time
from concurrent.futures import ProcessPoolExecutor
from .core import *

def one(args):
    setpath, outdir, tag = args
    o = json.load(open(setpath))
    pd = o["problems"][tag]
    pr = Problem(n=pd["n"], cap=pd["cap"], mnl=[tuple(m) for m in pd["mnl"]], edges=[tuple(e) for e in pd["edges"]], name=pd["name"])
    recs = sorted({d["a"] for d in o["decisions"] if d["src"] == tag} | {d["b"] for d in o["decisions"] if d["src"] == tag})
    ref = labels_of(pr.n, pr.cap, pr.mnl, pr.edges)
    rec = dict(tag=tag, F=pr.F, E=pr.E, M=pr.M, n=pr.n, cap=pr.cap)
    # untraced baselines: plain input (verified net), same annotated book
    rec["plain_depth"] = run_untraced_plain(pr, "depth")
    rec["plain_run"] = run_untraced_plain(pr, "run")
    rec["same_book_depth"] = run_untraced_same_book(pr)
    for mode in (2, 1):
        toks, sets, st = run_traced(pr, mode)
        tree = parse_tokens(toks)
        els = list_elems(tree, sets)
        labels = [tree[1][h] for h, _ in els]
        rec[f"mode{mode}"] = dict(stats=st, labels_ok=(labels == ref), n_labels=len(labels),
                                  sets={str(r): sorted(els[r][1]) for r in recs},
                                  all_sizes=[len(t) for _, t in els][:: max(1, len(els) // 200)])
    json.dump(rec, open(os.path.join(outdir, tag + ".json"), "w"))
    return tag, rec["mode2"]["stats"]["wall"], rec["mode2"]["labels_ok"]

if __name__ == "__main__":
    setpath, outdir = sys.argv[1], sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    os.makedirs(outdir, exist_ok=True)
    o = json.load(open(setpath))
    tags = sorted({d["src"] for d in o["decisions"]})
    with ProcessPoolExecutor(workers) as ex:
        for r in ex.map(one, [(setpath, outdir, t) for t in tags]):
            print(r, flush=True)
