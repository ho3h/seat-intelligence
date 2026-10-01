"""Same-data baseline: the RECON-SWING net (runs/exp10/t5_reconcile_canon.hvm, linked-list candidate input as the corpus
interface delivers it) on the same OpenSanctions slices. Depth oracle for depth, Rust interpreter + digest for correctness.
usage: python3 -m genome.exp16.baseline_list N..."""
import json, os, sys
from .data import slice_
from .run import reference, _timed, _parse, HVM, HVM_DEPTH, ROOT, RUNS
from ..corpus import load_all
from ..verify import assemble, assemble_digest
from ..digest import py_digest
from ..types import decode, tup, u24
P = load_all()["t5_reconcile_canon"]
NET = open(os.path.join(ROOT, "runs/exp10/t5_reconcile_canon.hvm")).read()
for N in map(int, sys.argv[1:]):
    s = slice_(N); canon, _ = reference(s)
    x = (s["n"], s["tau"], [(u, v, sc) for u, v, sc in s["edges"]])
    assert P.ref(x) == canon
    rec = dict(net="exp10_list", N=N, m_edges=len(s["edges"]))
    for mode, text, exe in (("depth", assemble(P, NET, x), HVM_DEPTH), ("rust", assemble_digest(P, NET, x), HVM)):
        path = os.path.join(ROOT, "scratch", f"exp16_bl_{os.getpid()}.hvm"); open(path, "w").write(text)
        try: out, err, wall, rss = _timed([exe, "run", path], 3600)
        finally: os.unlink(path)
        r = _parse(out)
        if mode == "depth": rec.update(depth=r["depth"], itrs_bare=r["itrs"], depth_err=None if r["depth"] else (err or out)[-300:])
        else:
            ok = r["result"] is not None and decode(r["result"], tup(u24, u24)) == py_digest(canon, P.out)
            rec.update(rust_secs=r["time"], itrs=r["itrs"], max_rss_mb=round(rss / 2**20, 1), correct=ok,
                       err=None if ok else (err or out)[-300:])
    print(json.dumps(rec), flush=True)
    with open(os.path.join(RUNS, "baseline_list.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
