"""Depth/interactions of a net on the verifier's seed-s large cases, with input stats.
usage: python3 runs/exp10/probe.py <prog> <net> [seed] [--cases big|all]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genome.verify import build_cases, assemble
from genome.executor import run_net
from genome.corpus import load_all
from concurrent.futures import ThreadPoolExecutor

def lp_rounds(n, pairs):
    adj = [[] for _ in range(n)]
    for u, v in pairs: adj[u].append(v); adj[v].append(u)
    lab = list(range(n)); r = 0
    while True:
        new = [max([lab[i]] + [lab[j] for j in adj[i]]) for i in range(n)]
        if new == lab: return r
        lab = new; r += 1

def stats(prog, x):
    if prog.startswith("t5_cluster") and isinstance(x[-1], list):
        n = x[0]; ps = x[-1]
        if ps and len(ps[0]) == 3: ps = [(u, v) for u, v, s in ps if s >= x[1]]
        return f"n={n} m={len(x[-1])} rounds={lp_rounds(n, ps)}"
    if prog.startswith("t5_reconcile"):
        n, tau = x[0], x[1]; cs = x[-1] if prog == "t5_reconcile_canon" else x[3]
        ps = [(u, v) for u, v, s in cs if s >= tau]
        return f"n={n} m={len(cs)} acc={len(ps)} rounds={lp_rounds(n, ps)}"
    return ""

if __name__ == "__main__":
    prog, net = sys.argv[1], sys.argv[2]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    p = load_all()[prog]; book = open(net).read()
    cases = [c for c in build_cases(p, seed) if c[0] == "big"]
    def one(c):
        r = run_net(assemble(p, book, c[2]), "depth", 240)
        return f"depth={r.depth} itrs={r.itrs} ok={r.ok} {stats(prog, c[2])} {r.error[:100]}"
    with ThreadPoolExecutor(3) as ex:
        for s in ex.map(one, cases): print(s, flush=True)
