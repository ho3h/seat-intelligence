"""Step-type counts (same / skip / merge) of the ordered greedy on the verifier's big cases, seed 0."""
import sys, os
sys.path.insert(0, os.getcwd())
from genome.corpus import load_all
from genome.verify import build_cases
from genome.corpus.t5_b import _decide, _find
P = load_all()
for pid in ["t5_conflict_greedy", "t5_conflict_greedy_cap", "t5_reconcile_canon_mnl"]:
    for kind, n, x in build_cases(P[pid], 0):
        if kind != "big": continue
        if pid == "t5_conflict_greedy": n_, mnl, acc = x; cap = None
        elif pid == "t5_conflict_greedy_cap": n_, cap, mnl, acc = x
        else: n_, tau, mnl, cands = x; acc = [c for c in cands if c[2] >= tau]; cap = None
        order = sorted(acc, key=lambda t: (-t[2], t[0], t[1]))
        p = list(range(n_)); mem = {i: {i} for i in range(n_)}; st = [0, 0, 0]
        for u, v, _ in order:
            a, b = _find(p, u), _find(p, v)
            if a == b: st[0] += 1; continue
            A, B = mem[a], mem[b]
            if any((x in A and y in B) or (x in B and y in A) for x, y in mnl) or (cap is not None and len(A) + len(B) > cap):
                st[1] += 1; continue
            st[2] += 1; p[a] = b; mem[b] = A | B; del mem[a]
        print(pid, n_, "steps", len(order), "same/skip/merge", st)
