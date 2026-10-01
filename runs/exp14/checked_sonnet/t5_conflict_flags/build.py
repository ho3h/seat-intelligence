import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, GlueError, NUM, DEPTH, ANY, LIST, TRIE, TUP, HOLE, EDGE, INF

P = Program()
lg = P.lg()
zeros = P.const_trie("z0", 0)
orr = P.update("uor", "or")        # leaf |= P
sett = P.update("uset", "set")     # leaf := P
zq = P.mc_empty("zq")
rq = P.mc_request("rq")
dv = P.mc_deliver("dv")


# pass A: count the clustering list and rebuild two copies of it
def stepA(d, cnt, h1, h2, x):
    x1, x2 = d.fanout(x, 2)
    h1n = d.fill_cons(h1, x1)
    h2n = d.fill_cons(h2, x2)
    return d.op(cnt, "+", 1), h1n, h2n

def finA(d, cnt, h1, h2):
    d.fill(h1, d.nil())
    d.fill(h2, d.nil())
    return cnt
wa = P.stream("wa", stepA, finA, state=[("cnt", NUM), ("h1", HOLE(LIST(NUM))), ("h2", HOLE(LIST(NUM)))], elem=NUM)


# pass B1: T[c[i]] |= 2  (canonical marker)
def stepB1(d, L, T, x):
    L1, L2 = d.fanout(L, 2)
    return L2, d.call(orr, t=T, k=x, L=L1, P=2)

def finB1(d, L, T):
    d.erase(L)
    return T
wb1 = P.stream("wb1", stepB1, finB1, state=[("L", DEPTH), ("T", TRIE(NUM))], elem=NUM)


# pass B2: C[i] := c[i]
def stepB2(d, L, i, C, x):
    L1, L2 = d.fanout(L, 2)
    i1, i2 = d.fanout(i, 2)
    C2 = d.call(sett, t=C, k=i1, L=L1, P=x)
    return L2, d.op(i2, "+", 1), C2

def finB2(d, L, i, C):
    d.erase(L, i)
    return C
wb2 = P.stream("wb2", stepB2, finB2, state=[("L", DEPTH), ("i", NUM), ("C", TRIE(NUM))], elem=NUM)


# pass M: for each must-not-link pair look up both clusters, set flag bit at cluster if equal
def stepM(d, L, q, T, C, a, b):
    L1, L2, L3, L4 = d.fanout(L, 4)
    ra, q1 = d.call(rq, q=q, k=a, L=L1)
    rb, q2 = d.call(rq, q=q1, k=b, L=L2)
    ra1, ra2 = d.fanout(ra, 2)
    eq = d.op(ra1, "=", rb)
    T2 = d.call(orr, t=T, k=ra2, L=L3, P=eq)
    return L4, q2, T2, C

def finM(d, L, q, T, C):
    d.call(dv, v=C, q=q, L=L)
    return T
wm = P.stream("wm", stepM, finM,
              state=[("L", DEPTH), ("q", P.prims["zq"].outputs[0].kind), ("T", TRIE(NUM)), ("C", TRIE(NUM))], elem=EDGE)


def fleaf(d, x, i, acc):
    d.erase(i)
    x1, x2 = d.fanout(x, 2)
    cond = d.op(x1, ">", 1)
    bit = d.op(x2, "&", 1)
    def no(b, bit, acc):
        b.erase(bit)
        return acc
    def yes(b, cm1, bit, acc):
        b.erase(cm1)
        return b.cons(bit, acc)
    return d.branch(cond, no, yes, bit, acc)
fl = P.fold("fl", fleaf, acc=LIST(NUM))


def prog(d, cl, es):
    v1, h1 = d.hole(LIST(NUM))
    v2, h2 = d.hole(LIST(NUM))
    n = d.call(wa, list=cl, init=(0, h1, h2))

    def empty(b, v1, v2, es):
        b.erase(v1, v2, es)
        return b.nil()

    def nonempty(b, nm1, v1, v2, es):
        L = b.call(lg, x=nm1)
        L1, L2, L3, L4, L5, L6, L7 = b.fanout(L, 7)
        C0 = b.call(zeros, L=L1)
        C = b.call(wb2, list=v2, init=(L2, 0, C0))
        T0 = b.call(zeros, L=L4)
        T1 = b.call(wb1, list=v1, init=(L3, T0))
        q0 = b.call(zq, L=L5)
        T2 = b.call(wm, list=es, init=(L6, q0, T1, C))
        return b.call(fl, t=T2, L=L7, acc=b.nil())
    return d.branch(n, empty, nonempty, v1, v2, es)

P.prog("t5_conflict_flags", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
