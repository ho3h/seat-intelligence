"""HERO-3 scaling measurements on the depth oracle (physics/hvm2-depth): rounds (parallel depth) and interactions at
n = 1k, 10k, 100k, for the rewritten tree net (balanced rope), the original sequential list net, the original after the
swing-18 K=16 lookahead transformation, the sequential in-order fold over the same rope (control), the list->rope->fold
ingest pipeline, and (5 folds) the strong Bend tree reduction on the same rope.
usage: python -m genome.hero3.scale <kind> [--sizes 1000,10000,100000] [fold ids ...]"""
from __future__ import annotations
import json, math, os, random, sys, time
from concurrent.futures import ThreadPoolExecutor
from ..executor import run_net
from ..verify import assemble
from .. import bend_io as B
from . import folds as F
from .nets import seq_net, tree_net, seqtree_net, ingest_net
from .programs import list_program, tree_program, build_rope

OUT = "runs/hero3"
SIZES = [1000, 10000, 100000]


def items(f, n, seed=5):
    rng = random.Random(seed * 1_000_003 + n)
    return [f.gen(rng) for _ in range(n)]


def measure(text, timeout):
    t = time.time()
    r = run_net(text, "depth", timeout)
    return dict(ok=r.ok, depth=r.depth, itrs=r.itrs, width=r.width, secs=round(time.time() - t, 1), error=(r.error or "")[:200], result=r.result[:80] if r.ok else "")


def run_one(kind, f, n, timeout=3000):
    xs = items(f, n)
    lp = list_program(f)
    if kind == "tree":
        tp = tree_program(f, "py")
        return measure(assemble(tp, tree_net(f), build_rope(xs, None, "balanced")), timeout)
    if kind == "seq_list":
        return measure(assemble(lp, seq_net(f), xs), timeout)
    if kind == "seq_author":
        from ..exp12.evaluate import native_nets
        return measure(assemble(lp, open(native_nets()[f.corpus]).read(), xs), timeout)
    if kind == "seq_la":
        from ..exp12.lookahead import transform
        net, _ = transform(seq_net(f), 16)
        return measure(assemble(lp, net, xs), timeout)
    if kind == "seq_tree":
        tp = tree_program(f, "py")
        return measure(assemble(tp, seqtree_net(f), build_rope(xs, None, "balanced")), timeout)
    if kind == "ingest_la":
        from ..exp12.lookahead import transform
        net, _ = transform(ingest_net(f), 16)
        return measure(assemble(lp, net, xs), timeout)
    if kind == "ingest":
        return measure(assemble(lp, ingest_net(f), xs), timeout)
    if kind == "bend":
        from .bend_trees import BEND
        tp = tree_program(f, "py")
        book, err = B.compile_bend(B.bend_source(tp, BEND[f.id]))
        if err: return dict(ok=False, error=err[:200])
        return measure(B.assemble_bend(tp, book, build_rope(xs, None, "balanced"), digest=False), timeout)
    raise ValueError(kind)


def main(argv):
    kind = argv[0]; sizes = SIZES; ids = []
    rest = argv[1:]
    if rest and rest[0] == "--sizes": sizes = [int(x) for x in rest[1].split(",")]; rest = rest[2:]
    ids = rest
    fs = [f for f in F.FOLDS if (f.id in ids if ids else f.label == "assoc")]
    if kind == "seq_author": fs = [f for f in fs if f.corpus]
    path = f"{OUT}/scale_{kind}.jsonl"
    done = set()
    if os.path.exists(path):
        for l in open(path):
            j = json.loads(l)
            if j.get("ok"): done.add((j["fold"], j["n"]))
    jobs = [(f, n) for n in sizes for f in fs if (f.id, n) not in done]

    def go(job):
        f, n = job
        rec = run_one(kind, f, n)
        rec.update(fold=f.id, kind=kind, n=n)
        return rec
    workers = int(os.environ.get("H3_WORKERS", "3"))
    with ThreadPoolExecutor(workers) as ex:
        for rec in ex.map(go, jobs):
            print(json.dumps({k: rec[k] for k in ("fold", "n", "ok", "depth", "itrs", "secs", "error") if k in rec}), flush=True)
            with open(path, "a") as fh: fh.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
