"""Depth of the Bend `full` program with its output folded inside the program (swing 27).

Why: the depth oracle's bare-output run of `full` at N=100k stops after 499M interactions at depth 1,805 (repeatable),
while the Rust interpreter and the oracle with the harness digest attached do ~835M and are exact. Any consumer on the
output makes the oracle do the whole job. So for `full` we also report the oracle depth of the same program whose three
outputs are reduced to one number inside Bend: a tree sum over the final-label trie (the canon values of all
vertices that have a trie leaf, depth O(log n))
plus sums over the 27-element conflict list and the ~15-element skipped list. The number is checked against Python.
usage: python3 -m genome.exp21.sumout N...   (appends var=full_sumout, mode=depth records to runs/exp21/results.jsonl)
"""
import json, os, re, subprocess, sys
from .run import source, assemble, HVM_DEPTH, RUNS, ROOT
from ..bend_io import compile_bend
from ..exp16.data import slice_
from ..exp16.run import reference_full, _timed

EXTRA = '''
def tsum(t):
  match t:
    case O/OEmp:
      return 0
    case O/OLf:
      return t.x
    case O/ONode:
      return tsum(t.l) + tsum(t.r)

def lsum(l):
  match l:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b, c) = l.head
      return a + b + c + lsum(l.tail)

def lsum2(l):
  match l:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = l.head
      return a + b + lsum2(l.tail)
'''

if __name__ == "__main__":
    K = int(os.environ.get("K", "4"))
    src = source(K, "full")
    old = "  return (tl(fins, L, z, n, []), cf, sk)"
    assert old in src
    src = src.replace(old, "  return tsum(fins) + z + lsum(cf) + lsum2(sk)") + EXTRA
    book, err = compile_bend(src)
    if err: raise SystemExit(err)
    for N in map(int, sys.argv[1:]):
        s = slice_(N); g, conf, sk = reference_full(s)
        # tsum covers the vertices that have a trie leaf (an accepted edge or a must-not-link pair); the others are
        # leafless in the trie (their canon is their own id, emitted by `ids` in the list version)
        leafy = {x for u, v, sc in s["edges"] if sc >= s["tau"] for x in (u, v)} | {x for a, b in s["mnl"] for x in (a, b)}
        want = (sum(g[i] for i in leafy) + sum(a + b + c for a, b, c in conf) + sum(u + v for u, v in sk)) % (1 << 24)
        text, meta = assemble(s, book, digest=False, full=True)
        path = os.path.join(ROOT, "scratch", f"exp21_sumout_{N}_{os.getpid()}.hvm")
        open(path, "w").write(text)
        try:
            out, errt, wall, rss = _timed(["env", "GENOME_READBACK=1", HVM_DEPTH, "run", path], 7200)
        finally:
            os.unlink(path)
        f = lambda p: (lambda m: m.group(1) if m else None)(re.search(p, out, re.M))
        rec = dict(arm="bend", var="full_sumout", k=K, mode="depth", N=N, **meta, itrs=int(f(r"^- ITRS: (\d+)") or 0),
                   depth=int(f(r"^- DEPTH: (\d+)") or 0), max_rss_mb=round(rss / 2**20, 1), result=f(r"^Result: (\S+)"),
                   want=want)
        rec["correct"] = rec["result"] == str(want)
        print(json.dumps(rec), flush=True)
        with open(os.path.join(RUNS, "results.jsonl"), "a") as fh: fh.write(json.dumps(rec) + "\n")
