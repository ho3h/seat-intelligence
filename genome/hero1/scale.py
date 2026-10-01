"""HERO-1 scale test: one policy on n synthetic guests; net output vs Python reference; depth (oracle), interactions, wall-clock
on the arm64 C runtime (HVM2 hvm.c compiled -O3 -mcpu=native, book passed as data, exp16 driver).

  python3 -m genome.hero1.scale <mode> <policy-name> n [n ...]     mode: rust | depth | native | ref
Appends JSON lines to runs/hero1/scale.jsonl.
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os, sys, time
sys.path.insert(0, _REPO)
from genome.hero1.lang import parse, to_text, prep, ref_sections, assign_ref, violations_fast, order_inversions_fast
from genome.hero1.guests import gen_guests
from genome.hero1 import sectioner as S
from genome.digest import gen_digest, py_digest
from genome.types import decode
from genome.exp16.run import HVM, HVM_DEPTH, driver, book_buffer, _timed, _parse
ROOT = _REPO
OUTF = os.path.join(ROOT, "runs/hero1/scale.jsonl")
CH = 100   # guests per input chunk definition

POLICIES = {
    "P1": "size 5\ntogether company\nlimit government 2\napart ai_lab big_tech\napart chips investor\norder ai_lab chips",
    "P2": "size 4\ntogether company\ntogether government\nlimit investor 1\napart software_security big_tech\norder investor",
}


def enc_input(x):
    cap, rules, guests = x
    defs = []
    cells = [f"({c} {s})" for c, s in guests]
    tail = "(0 *)"
    # chunk from the back so each chunk ends with a ref to the next
    chunks = [cells[i:i + CH] for i in range(0, len(cells), CH)] or [[]]
    for j in range(len(chunks) - 1, -1, -1):
        body = "".join(f"(1 ({c} " for c in chunks[j]) + tail + "))" * len(chunks[j])
        if j == 0: root_g = body
        else:
            name = f"__g{j}"; defs.append(f"@{name} = {body}"); tail = f"@{name}"
    rl = "(0 *)"
    for a, b, k in reversed(rules): rl = f"(1 (({a} ({b} {k})) {rl}))"
    return f"({cap} ({rl} {root_g}))", defs


def book(x, digest=True):
    root, defs = enc_input(x)
    if digest:
        dbook, droot = gen_digest(S.OUT)
        main = f"@main = r\n  & @prog ~ ({root} o)\n  & @{droot} ~ (o ((0 0) r))\n"
    else:
        dbook, main = "", f"@main = r\n  & @prog ~ ({root} r)\n"
    return main + "\n" + "\n".join(defs) + "\n\n" + S.net_text() + "\n\n" + dbook


def run(mode, pname, n, seed=7, mix="balanced", timeout=7200):
    pol = parse(POLICIES[pname]) if pname in POLICIES else parse(pname)
    g = gen_guests(n, seed, mix)
    rec = dict(mode=mode, policy=pname, n=n, seed=seed, mix=mix, program=to_text(pol).replace("\n", "; "))
    t0 = time.time(); seq = prep(g, pol); rec["prep_secs"] = round(time.time() - t0, 3)
    elems = [(c, s) for _, c, s in seq]
    t0 = time.time(); secs = ref_sections(pol.cap, pol.rules(), elems); rec["py_ref_secs"] = round(time.time() - t0, 3)
    assign = [None] * n
    for (i, _, _), sc in zip(seq, secs): assign[i] = sc
    rec["sections"] = max(secs) + 1 if secs else 0
    v = violations_fast(g, pol, assign); v["order"] = order_inversions_fast(g, pol, assign); rec["violations"] = v
    rec["violations_total"] = sum(v[k] for k in ("cap", "limit", "apart", "together", "order"))
    want = py_digest(secs, S.OUT)
    if mode == "ref": return rec
    x = (pol.cap, pol.rules(), elems)
    text = book(x, digest=(mode not in ("depth", "full"))); rec["book_bytes"] = len(text)
    path = os.path.join(ROOT, "scratch", f"hero1_{mode}_{pname}_{n}_{os.getpid()}.hvm")
    open(path, "w").write(text)
    try:
        if mode in ("rust", "full"): out, err, wall, rss = _timed([HVM, "run", path], timeout)
        elif mode == "depth": out, err, wall, rss = _timed([HVM_DEPTH, "run", path], timeout)
        elif mode == "native":
            exe = driver(); buf = path + ".bin"
            t = time.time(); rec["buf_bytes"] = book_buffer(text, buf); rec["serialise_secs"] = round(time.time() - t, 1)
            out, err, wall, rss = _timed(["arch", "-arm64", exe, buf], timeout)
            os.unlink(buf)
    finally:
        os.unlink(path)
    r = _parse(out)
    rec.update(itrs=r["itrs"], rt_secs=r["time"], wall=round(wall, 2), max_rss_mb=round(rss / 2**20, 1), depth=r["depth"], width=r["width"])
    if mode == "depth":
        rec["ok_run"] = r["depth"] is not None
        if not rec["ok_run"]: rec["err"] = (err or out)[-400:]
    elif mode == "full":
        try: got = decode(r["result"], S.OUT) if r["result"] else None
        except Exception as e: got = f"undecodable: {e}"
        rec["exact_full_decode"] = got == secs
        if not rec["exact_full_decode"]: rec["err"] = "full decode differs"
    else:
        try: got = decode(r["result"], __import__("genome.types", fromlist=["tup"]).tup(S.u24, S.u24)) if r["result"] else None
        except Exception as e: got = f"undecodable: {e}"
        rec["digest_ok"] = got == want
        if not rec["digest_ok"]: rec["err"] = f"got {got} want {want} :: " + (err or out)[-400:]
    return rec


if __name__ == "__main__":
    mode, pname = sys.argv[1], sys.argv[2]
    for n in map(int, sys.argv[3:]):
        rec = run(mode, pname, n)
        print(json.dumps(rec), flush=True)
        with open(OUTF, "a") as f: f.write(json.dumps(rec) + "\n")
