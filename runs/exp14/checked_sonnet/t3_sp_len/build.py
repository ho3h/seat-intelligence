import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, ADJ, EDGE, INF

P = Program()
lg = P.lg()
adj = P.adjacency()
empty_adj = P.empty_adj()
sp = P.sssp("sp")
gt = P.get("gt")


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
        b.erase(s, t, es)
        return 0

    def nonempty(b, nm1, s, t, es):
        nm1a, nm1b = b.fanout(nm1, 2)
        n = b.op(nm1b, "+", 1)
        L = b.call(lg, x=nm1a)
        L1, L2, L3, L4 = b.fanout(L, 4)
        G = b.call(w, list=es, init=(L2, b.call(empty_adj, L=L1)))
        D = b.call(sp, n=n, s=s, L=L3, G=G)
        return b.call(gt, t=D, k=t, L=L4)
    return d.branch(n, empty, nonempty, s, t, es)


P.prog("t3_sp_len", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
