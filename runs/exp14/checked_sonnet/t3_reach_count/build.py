import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, ADJ, EDGE, INF

P = Program()
lg = P.lg()
adj = P.adjacency()
empty_adj = P.empty_adj()
sp = P.sssp("sp")


def leaf(d, x, i, n):
    a = d.op(x, "!", INF)
    b = d.op(i, "<", n)
    return d.op(a, "&", b)
cnt = P.reduce("cnt", leaf, "+", index=True, env=NUM)


def step(d, L, g, u, v):
    L1, L2 = d.fanout(L, 2)
    g2 = d.call(adj, G=g, u=u, L=L1, v=v, w=1)
    return L2, g2


def fin(d, L, g):
    d.erase(L)
    return g
w = P.stream("w", step, fin, state=[("L", DEPTH), ("g", ADJ)], elem=EDGE)


def prog(d, n, s, es):
    def empty(b, s, es):
        b.erase(s, es)
        return 0

    def nonempty(b, nm1, s, es):
        nm1a, nm1b = b.fanout(nm1, 2)
        n = b.op(nm1b, "+", 1)
        n1, n2 = b.fanout(n, 2)
        L = b.call(lg, x=nm1a)
        L1, L2, L3, L4 = b.fanout(L, 4)
        G = b.call(w, list=es, init=(L2, b.call(empty_adj, L=L1)))
        D = b.call(sp, n=n1, s=s, L=L3, G=G)
        return b.call(cnt, t=D, L=L4, E=n2)
    return d.branch(n, empty, nonempty, s, es)

P.prog("t3_reach_count", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
