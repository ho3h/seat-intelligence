import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, ADJ, EDGE, INF

P = Program()
lg = P.lg()
cc = P.relax("cc")
adj = P.adjacency()
empty_adj = P.empty_adj()
infs = P.const_trie("gl_inf", INF)
iota = P.iota_trie("io")
tl = P.to_list("tl")


def step(d, L, g, u, v):
    L1, L2, L3 = d.fanout(L, 3)
    u1, u2 = d.fanout(u, 2)
    v1, v2 = d.fanout(v, 2)
    g2 = d.call(adj, G=g, u=u1, L=L1, v=v1, w=0)
    g3 = d.call(adj, G=g2, u=v2, L=L2, v=u2, w=0)
    return L3, g3


def fin(d, L, g):
    d.erase(L)
    return g
w = P.stream("w", step, fin, state=[("L", DEPTH), ("g", ADJ)], elem=EDGE)


def prog(d, n, es):
    def empty(b, es):
        b.erase(es)
        return b.nil()

    def nonempty(b, nm1, es):
        nm1a, nm1b = b.fanout(nm1, 2)
        nn = b.op(nm1b, "+", 1)
        L = b.call(lg, x=nm1a)
        L1, L2, L3, L4, L5, L6 = b.fanout(L, 6)
        G = b.call(w, list=es, init=(L2, b.call(empty_adj, L=L1)))
        D = b.call(cc, G=G, D=b.call(infs, L=L3), C=b.call(iota, L=L4), L=L5)
        return b.call(tl, t=D, L=L6, n=nn)
    return d.branch(n, empty, nonempty, es)


P.prog("t3_cc_label", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
