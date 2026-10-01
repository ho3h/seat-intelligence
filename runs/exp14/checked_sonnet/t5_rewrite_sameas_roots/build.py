import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, MCQ, LIST, HOLE, INF

ROUNDS = 8   # pointer doubling: 2^8 = 256 >= any chain here (n <= 144)

P = Program()
lg = P.lg()
zeros = P.const_trie("z0", 0)
mce = P.mc_empty("zq")
setv = P.update("vset", "set")
rq = P.mc_request("rq")
dv = P.mc_deliver("dv")


def step(d, L, i, V, q, h, x):
    L1, L2, L3 = d.fanout(L, 3)
    i1, i2 = d.fanout(i, 2)
    x1, x2 = d.fanout(x, 2)
    V2 = d.call(setv, t=V, k=i1, L=L1, P=x1)
    r, q2 = d.call(rq, q=q, k=x2, L=L2)
    h2 = d.fill_cons(h, r)
    return L3, d.op(i2, "+", 1), V2, q2, h2


def fin(d, L, i, V, q, h):
    d.erase(i)
    d.fill(h, d.nil())
    d.call(dv, v=V, q=q, L=L)
    return 0


w = P.stream("w", step, fin,
             state=[("L", DEPTH), ("i", NUM), ("V", TRIE(NUM)), ("q", MCQ), ("h", HOLE(LIST(NUM)))],
             elem=NUM)


def cstep(d, c, h, x):
    return d.op(c, "+", 1), d.fill_cons(h, x)


def cfin(d, c, h):
    d.fill(h, d.nil())
    return c


cw = P.stream("cw", cstep, cfin, state=[("c", NUM), ("h", HOLE(LIST(NUM)))], elem=NUM)


def prog(d, inp):
    val, hole = d.hole(LIST(NUM))
    n = d.call(cw, list=inp, init=(0, hole))

    def empty(b, es):
        b.erase(es)
        return b.nil()

    def nonempty(b, nm1, es):
        L = b.call(lg, x=nm1)
        Ls = list(b.fanout(L, 3 * ROUNDS))
        cur = es
        for _ in range(ROUNDS):
            val, hole = b.hole(LIST(NUM))
            V = b.call(zeros, L=Ls.pop())
            q = b.call(mce, L=Ls.pop())
            res = b.call(w, list=cur, init=(Ls.pop(), 0, V, q, hole))
            b.erase(res)
            cur = val
        return cur
    return d.branch(n, empty, nonempty, val)


P.prog("t5_rewrite_sameas_roots", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
