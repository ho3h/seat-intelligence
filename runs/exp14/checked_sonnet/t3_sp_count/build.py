import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, GlueError, NUM, DEPTH, ANY, LIST, TRIE, TUP, HOLE, EDGE, WEDGE, ADJ, INF, MCQ

# Count shortest directed paths s -> t.
# 1. one walk over the edge list builds: g1 (all edges, w=1) for sssp, g2 (DAG adjacency whose weight is the flag
#    D[u]+1 == D[v]; D looked up through mc_request wires), and the request trie q.
# 2. everything else happens in fin: sssp on g1 -> D; mc_deliver(D, q); then a level-synchronous count wave
#    over g2 (state = count, message = count * flag, combiner add); answer = count[t].
P = Program()
lg = P.lg()
adj = P.adjacency()
empty_adj = P.empty_adj()
mce = P.mc_empty("zq")
rq = P.mc_request("rq")
dv = P.mc_deliver("dv")
sp = P.sssp("sp")
zeros = P.const_trie("z0", 0)
uadd = P.update("uadd", "add")
gt = P.get("gt")


def act(d, X, dvv, c):
    d.erase(X)
    c1, c2, c3 = d.fanout(c, 3)
    d2 = d.op(dvv, "+", c1)
    flag = d.op(c2, "!", 0)
    return d2, flag, c3


def msg(d, m, w):
    return d.op(m, "*", w)


fr = P.frontier("fr", act, msg, "add", 0)


def step(d, L, n, s, t, g1, g2, q, u, v):
    L1, L2, L3, L4, L5 = d.fanout(L, 5)
    u1, u2, u3 = d.fanout(u, 3)
    v1, v2, v3 = d.fanout(v, 3)
    g1b = d.call(adj, G=g1, u=u1, L=L1, v=v1, w=1)
    ru, q1 = d.call(rq, q=q, k=u3, L=L2)
    rv, q2 = d.call(rq, q=q1, k=v3, L=L3)
    ru1 = d.op(ru, "+", 1)
    flag = d.op(ru1, "=", rv)
    g2b = d.call(adj, G=g2, u=u2, L=L4, v=v2, w=flag)
    return L5, n, s, t, g1b, g2b, q2


def fin(d, L, n, s, t, g1, g2, q):
    L1, L2, L3, L4, L5, L6, L7 = d.fanout(L, 7)
    s1, s2 = d.fanout(s, 2)
    D = d.call(sp, n=n, s=s1, L=L1, G=g1)
    d.call(dv, v=D, q=q, L=L2)
    z1 = d.call(zeros, L=L3)
    z2 = d.call(zeros, L=L4)
    C = d.call(uadd, t=z2, k=s2, L=L5, P=1)
    D2 = d.call(fr, G=g2, D=z1, C=C, L=L6, X=0)
    return d.call(gt, t=D2, k=t, L=L7)


w = P.stream("w", step, fin,
             state=[("L", DEPTH), ("n", NUM), ("s", NUM), ("t", NUM), ("g1", ADJ), ("g2", ADJ), ("q", MCQ)],
             elem=EDGE)


def prog(d, n, s, t, es):
    def empty(b, s, t, es):
        b.erase(s, t, es)
        return 0

    def nonempty(b, nm1, s, t, es):
        nm1a, nm1b = b.fanout(nm1, 2)
        n = b.op(nm1b, "+", 1)
        L = b.call(lg, x=nm1a)
        L1, L2, L3, L4 = b.fanout(L, 4)
        g1 = b.call(empty_adj, L=L1)
        g2 = b.call(empty_adj, L=L2)
        q = b.call(mce, L=L3)
        return b.call(w, list=es, init=(L4, n, s, t, g1, g2, q))
    return d.branch(n, empty, nonempty, s, t, es)


P.prog("t3_sp_count", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
