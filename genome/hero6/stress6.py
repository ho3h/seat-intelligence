"""HERO-6 kernel checks beyond the hidden suite.
 (a) N random kernel inputs (sizes up to 300, tag masks with 0-17 name bits), net vs ref_tags;
 (b) M random policies WITH avoid/pair (and old words) on random named guest lists and on the real 34:
     net (tag input) assignment == lang6.assign_ref (the JS-semantics reference).
  python3 -m genome.hero6.stress6 [N] [M] [seed]"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import random, sys, time, json
sys.path.insert(0, _REPO)
from concurrent.futures import ThreadPoolExecutor
from genome.hero6 import sectioner6 as S
from genome.hero6 import lang6 as L
from genome.hero6.selftest6 import rand_guests, rand_pol
from genome.verify import assemble
from genome.executor import run_net
from genome.types import decode


def run_assign(g, pol, p=None):
    x, seq = L.tag_input(g, pol)
    rr = run_net(assemble(p or S.make_program(), S.net_text(), x), "run", 60)
    if not rr.ok: return None
    secs = decode(rr.result, S.OUT); a = [None] * len(g)
    for (i, _, _), s in zip(seq, secs): a[i] = s
    return a


def main(N=5000, M=1000, seed=600):
    p = S.make_program(); r = random.Random(seed)
    cases = [S._gen(r, r.choice([0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 100, 200, 300])) for _ in range(N)]
    def one(x):
        rr = run_net(assemble(p, S.net_text(), x), "run", 60)
        return rr.ok and decode(rr.result, S.OUT) == p.ref(x)
    t = time.time()
    with ThreadPoolExecutor(3) as ex: res = list(ex.map(one, cases))
    ka = sum(res); print(f"(a) kernel stress: {ka}/{N} net == ref_tags, seed {seed}, {time.time() - t:.0f}s", flush=True)
    real, _ = L.load_real()
    pols = []
    for k in range(M):
        g = real if k % 4 == 0 else rand_guests(r, r.choice([5, 12, 34, 60, 120]))
        pols.append((g, rand_pol(r, g)))
    def two(gp):
        g, pol = gp
        return run_assign(g, pol, p) == L.assign_ref(g, pol)
    t = time.time()
    with ThreadPoolExecutor(3) as ex: res2 = list(ex.map(two, pols))
    kb = sum(res2); na = sum(1 for _, q in pols if q.avoids); npr = sum(1 for _, q in pols if q.pairs)
    print(f"(b) pipeline: {kb}/{M} policies net assignment == reference (with avoid: {na}, with pair: {npr}; real 34 list: {M // 4}), {time.time() - t:.0f}s")
    json.dump(dict(kernel=[ka, N], pipeline=[kb, M], with_avoid=na, with_pair=npr, seed=seed), open(_REPO + "/runs/hero6/stress6.json", "w"))
    return ka == N and kb == M


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(0 if main(int(a[0]) if a else 5000, int(a[1]) if len(a) > 1 else 1000, int(a[2]) if len(a) > 2 else 600) else 1)
