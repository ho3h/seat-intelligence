"""Build net.hvm for t3_sp_len: shortest path length in an undirected graph.

Input (n, s, t, edges): undirected graph with n vertices, source s, target t, edge list.
Output: shortest path length from s to t (0 if s==t, INF if disconnected).
"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib.glue import Program, NUM, DEPTH, ADJ, EDGE, INF

def t3_sp_len():
    P = Program()
    lg = P.lg()
    empty_adj = P.empty_adj()
    adj = P.adjacency()
    sssp = P.sssp("sp")
    gt = P.get("gt")

    # Walker: build adjacency trie from edge list
    def step(d, L, g, u, v):
        L1, L2, L3 = d.fanout(L, 3)
        u1, u2 = d.fanout(u, 2)
        v1, v2 = d.fanout(v, 2)
        g2 = d.call(adj, G=g, u=u1, L=L1, v=v1, w=1)
        g3 = d.call(adj, G=g2, u=v2, L=L2, v=u2, w=1)
        return L3, g3

    def fin(d, L, g):
        d.erase(L)
        return g

    w = P.stream("w", step, fin, state=[("L", DEPTH), ("g", ADJ)], elem=EDGE)

    def prog(d, n, s, t, es):
        def empty(b, s, t, es):
            # n == 0: return INF
            b.erase(s, t, es)
            return INF

        def nonempty(b, nm1, s, t, es):
            # n > 0: build graph, run SSSP, extract distance to t
            nm1_a, nm1_b = b.fanout(nm1, 2)
            n = b.op(nm1_a, "+", 1)
            L = b.call(lg, x=nm1_b)
            L1, L2, L3, L4 = b.fanout(L, 4)

            # Build adjacency trie from edges
            G = b.call(w, list=es, init=(L1, b.call(empty_adj, L=L2)))

            # Run SSSP from source s
            D = b.call(sssp, n=n, s=s, L=L3, G=G)

            # Extract distance to target t
            dist = b.call(gt, t=D, k=t, L=L4)
            return dist

        return d.branch(n, empty, nonempty, s, t, es)

    P.prog("t3_sp_len", prog)
    return P

if __name__ == "__main__":
    path = os.path.join(D, "net.hvm")
    t3_sp_len().write(path)
    print("wrote", path)
