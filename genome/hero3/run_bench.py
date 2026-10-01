"""HERO-3 stage runner. usage: python -m genome.hero3.run_bench tester|verify [fold ids...]"""
from __future__ import annotations
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from ..verify import verify
from . import folds as F
from .tester import test_fold
from .nets import seq_net, tree_net
from .programs import list_program, tree_program

OUT = "runs/hero3"
os.makedirs(OUT + "/nets", exist_ok=True)


def stage_tester(ids):
    fs = [f for f in F.FOLDS if not ids or f.id in ids]
    res = {}
    if os.path.exists(f"{OUT}/stage1_tester.json"): res = json.load(open(f"{OUT}/stage1_tester.json"))

    def run(f):
        t = time.time()
        rs = [test_fold(f, seed) for seed in (7, 8, 9)]
        return f.id, rs, time.time() - t
    with ThreadPoolExecutor(4) as ex:
        for fid, rs, dt in ex.map(run, fs):
            res[fid] = rs
            f = F.by_id(fid)
            print(f"{fid:24s} {f.label:11s} accept={[r['accept'] for r in rs]} reasons={rs[0]['reject_reasons']} comm={rs[0]['commutative']} {dt:.1f}s", flush=True)
            json.dump(res, open(f"{OUT}/stage1_tester.json", "w"), indent=1)


def slim(r):
    return dict(status=r["status"], cases=r.get("cases"), failed=r.get("failed"), cex=r.get("counterexample"), reason=r.get("reason"), metrics=r.get("metrics"))


def stage_verify(ids):
    t1 = json.load(open(f"{OUT}/stage1_tester.json"))
    fs = [f for f in F.FOLDS if not ids or f.id in ids]
    res = {}
    if os.path.exists(f"{OUT}/stage2_verify.json"): res = json.load(open(f"{OUT}/stage2_verify.json"))

    def run(f):
        accept = all(r["accept"] for r in t1[f.id])
        orig = seq_net(f); tree = tree_net(f)
        open(f"{OUT}/nets/{f.id}_seq.hvm", "w").write(orig); open(f"{OUT}/nets/{f.id}_tree.hvm", "w").write(tree)
        rec = dict(fold=f.id, label=f.label, accepted=accept, seeds={}, audit={})
        tp = tree_program(f, "py")
        for s in (0, 1, 2):
            rec["seeds"][s] = slim(verify(tp, tree, s, workers=3))
        if accept:
            npg = tree_program(f, "net", orig)
            for s in (100, 101, 102):
                rec["audit"][s] = slim(verify(npg, tree, s, workers=3))
        return rec
    with ThreadPoolExecutor(2) as ex:
        for rec in ex.map(run, fs):
            res[rec["fold"]] = rec
            st = [v["status"] for v in rec["seeds"].values()]; au = [v["status"] for v in rec["audit"].values()]
            print(f"{rec['fold']:24s} {rec['label']:11s} accepted={rec['accepted']} seeds0-2={st} audit100-102={au}", flush=True)
            json.dump(res, open(f"{OUT}/stage2_verify.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    stage = sys.argv[1]; ids = sys.argv[2:]
    {"tester": stage_tester, "verify": stage_verify}[stage](ids)
