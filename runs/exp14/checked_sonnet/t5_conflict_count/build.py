import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, GlueError, NUM, DEPTH, ANY, LIST, TRIE, TUP, HOLE, EDGE, MCQ, INF

P = Program()
lg = P.lg()
zeros = P.const_trie("z0", 0)
setu = P.update("st", "set")
mce = P.mc_empty("zq")
rq = P.mc_request("rq")
dv = P.mc_deliver("dv")

# pass 1: copy the clustering list and count its length
def s1_step(d, cnt, hole, x):
    return d.op(cnt, "+", 1), d.fill_cons(hole, x)
def s1_fin(d, cnt, hole):
    d.fill(hole, d.nil())
    return cnt
w1 = P.stream("w1", s1_step, s1_fin, state=[("cnt", NUM), ("hole", HOLE(LIST(NUM)))], elem=NUM)

# pass 2: build trie T[i] = c[i]
def s2_step(d, L, i, T, x):
    L1, L2 = d.fanout(L, 2)
    i1, i2 = d.fanout(i, 2)
    T2 = d.call(setu, t=T, k=i1, L=L1, P=x)
    return L2, d.op(i2, "+", 1), T2
def s2_fin(d, L, i, T):
    d.erase(L, i)
    return T
w2 = P.stream("w2", s2_step, s2_fin, state=[("L", DEPTH), ("i", NUM), ("T", TRIE(NUM))], elem=NUM)

# pass 3: for each must-not-link pair look up c[a], c[b]
def s3_step(d, L, q, cnt, T, a, b):
    L1, L2, L3 = d.fanout(L, 3)
    ra, q1 = d.call(rq, q=q, k=a, L=L1)
    rb, q2 = d.call(rq, q=q1, k=b, L=L2)
    e = d.op(ra, "=", rb)
    return L3, q2, d.op(cnt, "+", e), T
def s3_fin(d, L, q, cnt, T):
    d.call(dv, v=T, q=q, L=L)
    return cnt
w3 = P.stream("w3", s3_step, s3_fin, state=[("L", DEPTH), ("q", MCQ), ("cnt", NUM), ("T", TRIE(NUM))], elem=EDGE)

def prog(d, cl, mnl):
    v, h = d.hole(LIST(NUM))
    n = d.call(w1, list=cl, init=(0, h))
    def empty(b, v, mnl):
        b.erase(v, mnl)
        return 0
    def nonempty(b, nm1, v, mnl):
        L = b.call(lg, x=nm1)
        L1, L2, L3, L4 = b.fanout(L, 4)
        T = b.call(w2, list=v, init=(L2, 0, b.call(zeros, L=L1)))
        q0 = b.call(mce, L=L3)
        return b.call(w3, list=mnl, init=(L4, q0, 0, T))
    return d.branch(n, empty, nonempty, v, mnl)
P.prog("t5_conflict_count", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
