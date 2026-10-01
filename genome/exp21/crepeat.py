"""C-runtime reliability check (swing 27): serialise a book once and run it R times on the arm64 C runtime (8 threads),
each under a hard kill after T seconds; report time, interactions and digest check per run.
usage: python3 -m genome.exp21.crepeat <bend:VAR|native:NET> N R [T]   -> runs/exp21/crepeat.jsonl"""
import json, os, re, subprocess, sys, time
from .run import compiled, assemble, RUNS, ROOT
from ..exp16.data import slice_
from ..exp16.run import reference, reference_full, book_buffer, driver, OUT_T, OUT_FULL, book as nbook
from ..exp16.net import build
from ..exp16.net_full import build as build_full
from ..digest import py_digest
from ..types import tup, u24, decode

arm, var = sys.argv[1].split(":"); N, R = int(sys.argv[2]), int(sys.argv[3]); T = int(sys.argv[4]) if len(sys.argv) > 4 else 120
full = var == "full"
s = slice_(N)
if full:
    g, c, sk = reference_full(s); want = py_digest((g, c, sk), OUT_FULL)
else:
    want = py_digest(reference(s), OUT_T)
if arm == "bend":
    text, _ = assemble(s, compiled(4, var), digest=True, full=full)
else:
    text, _ = nbook(s, build_full(2) if full else build(2, var), digest=True, full=full)
buf = os.path.join(ROOT, "scratch", f"exp21_crep_{os.getpid()}.bin"); book_buffer(text, buf); exe = driver()
try:
    for i in range(R):
        t = time.time()
        p = subprocess.run(["timeout", "-s", "KILL", str(T), "arch", "-arm64", exe, buf], capture_output=True, text=True)
        wall = time.time() - t
        m = re.search(r"^Result: (.*)$", p.stdout, re.M); it = re.search(r"^- ITRS: (\d+)", p.stdout, re.M)
        tm = re.search(r"^- TIME: ([\d.]+)s", p.stdout, re.M)
        try: got = decode(m.group(1), tup(u24, u24)) if m else None
        except Exception as e: got = f"undecodable {m.group(1)[:40]}"
        rec = dict(arm=arm, var=var, N=N, run=i, rc=p.returncode, wall=round(wall, 2), rt_secs=float(tm.group(1)) if tm else None,
                   itrs=int(it.group(1)) if it else None, correct=got == want, hung=p.returncode == -9 or p.returncode == 137)
        print(json.dumps(rec), flush=True)
        with open(os.path.join(RUNS, "crepeat.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
finally:
    os.unlink(buf)
