"""Swing 27 (G4 fairness): the reconciliation core written in Bend, fed the SAME input text as the native net of
genome/exp16 and run on the same runtimes (Rust interpreter, depth oracle, arm64 C runtime with the book loaded as data).

Input encoding: genome.exp16.run.encode_input produces `(n (L (tau (E (HE (M HM))))))` with E / M perfect binary trees of
CON pairs and leaves `(u (v s))` / `(a (b live))`. That text IS the Bend encoding of the tuple
(n, L, tau, E, HE, M, HM) with E a nested-pair tree of 3-tuples (Bend encodes tuples as plain CON pairs), so the Bend
program receives byte-for-byte the native input (same data, same tree shape, same spill definitions).
Output (canon list, conflict list) is Bend-encoded; the harness digest for Bend values (genome.bend_io.gen_digest_bend)
folds it to two numbers, compared with the Python union-find reference digest (genome.digest.py_digest), as in exp16.

usage: python3 -m genome.exp21.run <rust|depth|native> N [N ...]     env: K (speculative rounds, default 3), VAR
Results: runs/exp21/results.jsonl
"""
from __future__ import annotations
import hashlib, json, os, sys, time
from ..exp16.data import slice_
from ..exp16.run import (reference, reference_full, lp_stats, encode_input, book_buffer, driver, _timed, _parse,
                         HVM, HVM_DEPTH, OUT_T, OUT_FULL)
from ..bend_io import compile_bend, gen_digest_bend
from ..digest import py_digest
from ..types import tup, u24, decode

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(ROOT, "runs/exp21")


def source(k=3, var="recon"):
    src = open(os.path.join(HERE, f"{var}.bend.tmpl")).read()
    cons = "cell({}, {})" if "def cell(" in src else "List/Cons({}, {})"
    pre = "F"
    for _ in range(k): pre = cons.format(1, pre)
    if k < 0: pre = cons.format(0, "F")      # diagnostic only: zero LP rounds (setup + output cost; wrong output)
    return src.replace("__PRE__", pre)


def compiled(k=3, var="recon"):
    src = source(k, var)
    open(os.path.join(RUNS, f"{var}_k{k}.bend"), "w").write(src)
    book, err = compile_bend(src, timeout=300)
    if err: raise RuntimeError(err)
    open(os.path.join(RUNS, f"{var}_k{k}.hvm"), "w").write(book)
    return book


def assemble(s, bend_book, digest=True, full=False):
    root, defs, meta = encode_input(s, by_score=full)
    if digest:
        dbook, droot = gen_digest_bend(OUT_FULL if full else OUT_T)
        main = f"@main = r\n  & @prog ~ ({root} o)\n  & @{droot} ~ (o ((0 0) r))\n"
    else:
        dbook, main = "", f"@main = r\n  & @prog ~ ({root} r)\n"
    return main + "\n" + "\n".join(defs) + "\n\n" + bend_book + "\n\n" + dbook, meta


def run(mode, N, bend_book, timeout=7200, full=False, tag=""):
    s = slice_(N)
    canon, conf = reference(s)
    rec = dict(mode=mode, N=N, n=s["n"], m_edges=len(s["edges"]), accepted=sum(1 for e in s["edges"] if e[2] >= s["tau"]),
               mnl=len(s["mnl"]), conflicts_ref=len(conf))
    rec.update(lp_stats(s))
    if full:
        g, conf2, sk = reference_full(s); want = py_digest((g, conf2, sk), OUT_FULL); rec["skipped_ref"] = len(sk)
    else:
        want = py_digest((canon, conf), OUT_T)
    text, meta = assemble(s, bend_book, digest=(mode != "depth"), full=full); rec.update(meta)   # depthd: oracle + digest
    rec["book_bytes"] = len(text)
    path = os.path.join(ROOT, "scratch", f"exp21_{mode}_{N}_{os.getpid()}{tag}.hvm")
    open(path, "w").write(text)
    try:
        if mode == "rust":
            out, err, wall, rss = _timed([HVM, "run", path], timeout)
        elif mode in ("depth", "depthd"):
            pre = ["env", "GENOME_READBACK=1"] if mode == "depthd" else []   # digest output is two numbers: safe to read back
            out, err, wall, rss = _timed(pre + [HVM_DEPTH, "run", path], timeout)
        elif mode == "native":
            exe = driver(); buf = path + ".bin"
            t = time.time(); rec["buf_bytes"] = book_buffer(text, buf); rec["serialise_secs"] = round(time.time() - t, 1)
            out, err, wall, rss = _timed(["arch", "-arm64", exe, buf], timeout)
            os.unlink(buf)
        else:
            raise ValueError(mode)
    finally:
        os.unlink(path)
    r = _parse(out)
    rec.update(itrs=r["itrs"], rt_secs=r["time"], wall=round(wall, 2), max_rss_mb=round(rss / 2**20, 1),
               depth=r["depth"], width=r["width"])
    if mode == "depth":
        rec["ok_run"] = r["depth"] is not None
        if not rec["ok_run"]: rec["err"] = (err or out)[-400:]
    else:
        try:
            got = decode(r["result"], tup(u24, u24)) if r["result"] else None
        except Exception as e:
            got = f"undecodable: {e}"
        rec["correct"] = got == want
        if not rec["correct"]: rec["err"] = f"got {got} want {want} :: " + (err or out)[-400:]
    return rec


if __name__ == "__main__":
    mode = sys.argv[1]
    k = int(os.environ.get("K", "3")); var = os.environ.get("VAR", "recon")
    book = compiled(k, var)
    for N in map(int, sys.argv[2:]):
        rev = hashlib.sha1(source(k, var).encode()).hexdigest()[:8]
        rec = dict(arm="bend", var=var, k=k, rev=rev, tpc_l2=int(os.environ.get("TPC_L2", "3")) if mode == "native" else None,
                   **run(mode, N, book, full=(var == "full")))
        print(json.dumps(rec), flush=True)
        with open(os.path.join(RUNS, "results.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
