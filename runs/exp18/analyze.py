"""Workload statistics for the greedy kernels on the verifier's big cases (n = 72, 144)."""
import sys, os
sys.path.insert(0, os.getcwd())
from genome.corpus import load_all
from genome.verify import build_cases
from genome.corpus.t5_b import _decide
P = load_all()
def comps(n, edges):
    p = list(range(n))
    def f(x):
        while p[x] != x: p[x] = p[p[x]]; x = p[x]
        return x
    for u, v in edges: p[f(u)] = f(v)
    return [f(i) for i in range(n)]
for pid in ["t5_conflict_greedy", "t5_conflict_greedy_cap", "t5_reconcile_canon_mnl"]:
    p = P[pid]
    for seed in (0,):
        for kind, n, x in build_cases(p, seed):
            if kind != "big": continue
            if pid == "t5_conflict_greedy": n_, mnl, acc = x; cap = None
            elif pid == "t5_conflict_greedy_cap": n_, cap, mnl, acc = x
            else: n_, tau, mnl, cands = x; acc = _decide(tau, cands); cap = None
            c = comps(n_, [(u, v) for u, v, _ in acc])
            size = {}
            for r in c: size[r] = size.get(r, 0) + 1
            bad = {c[a] for a, b in mnl if c[a] == c[b]}
            if cap is not None: bad |= {r for r, s in size.items() if s > cap}
            ce = [e for e in acc if c[e[0]] in bad]
            per = {}
            for e in ce: per[c[e[0]]] = per.get(c[e[0]], 0) + 1
            print(pid, n_, "cap", cap, "m", len(acc), "mnl", len(mnl), "conf-edges", len(ce), "max per comp", max(per.values(), default=0), "ncomp", len(per), "largest comp", max(size.values()))
