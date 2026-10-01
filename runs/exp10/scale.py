"""Scaling of the channel-LP connected-components net (t5_cluster_canon) with input size.
Inputs: the corpus generator's world (true clusters of size 1-12 plus noisy random candidates), m = 2n candidates,
accepted at tau = 600 (fixed so sizes are comparable). usage: python3 runs/exp10/scale.py depth|native n..."""
import sys, os, random, time, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
from genome.verify import assemble
from genome.executor import run_net, run_native
from genome.corpus import load_all
from genome.corpus.t5_a import _cands
from genome.corpus import t5_a
from genome.types import decode

def lp_rounds(n, pairs):
    adj = [[] for _ in range(n)]
    for u, v in pairs: adj[u].append(v); adj[v].append(u)
    lab = list(range(n)); r = 0
    while True:
        new = [max([lab[i]] + [lab[j] for j in adj[i]]) for i in range(n)]
        if new == lab: return r, max((len(a) for a in adj), default=0)
        lab = new; r += 1

def case(n, seed=0):
    rng = random.Random(1000 + n + seed)
    ps = [(u, v) for u, v, s in _cands(rng, n, m=2 * n) if s >= 600]
    return (n, ps)

if __name__ == "__main__":
    mode = sys.argv[1]; P = load_all()["t5_cluster_canon"]
    net = open(os.path.join(ROOT, "runs/exp10/t5_cluster_canon.hvm")).read()
    for n in map(int, sys.argv[2:]):
        x = case(n); R, dmax = lp_rounds(n, x[1])
        exp = P.ref(x)
        t = time.time()
        if mode == "depth":
            r = run_net(assemble(P, net, x), "depth", 3000)
        else:
            r = run_native(assemble(P, net, x), 900, cflags=tuple(os.environ.get("CFLAGS", "-O3 -mcpu=native").split()))
        if mode == "depth":  # the oracle does not print results: check via the verifier's digest path
            from genome.verify import assemble_digest
            from genome.digest import py_digest
            from genome.types import tup, u24
            d = run_net(assemble_digest(P, net, x), "run", 3000)
            ok = d.ok and decode(d.result, tup(u24, u24)) == py_digest(exp, P.out)
        else:
            try: ok = r.ok and decode(r.result, P.out) == exp
            except Exception as e: ok = f"decode failed: {e}"
        print(json.dumps(dict(mode=mode, n=n, m=len(x[1]), lp_rounds=R, max_deg=dmax, depth=r.depth, itrs=r.itrs,
                              secs=r.secs, wall=round(time.time() - t, 1), correct=ok, err=r.error[:200],
                              depth_per_node=round(r.depth / n, 2), itrs_per_node=round(r.itrs / n, 1))), flush=True)
