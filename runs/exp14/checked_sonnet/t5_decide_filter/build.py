import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, GlueError, NUM, DEPTH, ANY, LIST, TRIE, TUP, HOLE, EDGE, WEDGE, ADJ, INF

P = Program()


def step(d, tau, hole, u, v, s):
    tau1, tau2 = d.fanout(tau, 2)
    s1, s2 = d.fanout(s, 2)
    rej = d.op(tau1, ">", s1)          # 1 if score < tau (reject)

    def keep(b, u, v, s, hole):
        return b.fill_cons(hole, (u, v, s))

    def drop(b, cm1, u, v, s, hole):
        b.erase(cm1, u, v, s)
        return hole
    h2 = d.branch(rej, keep, drop, u, v, s2, hole)
    return tau2, h2


def fin(d, tau, hole):
    d.erase(tau)
    d.fill(hole, d.nil())
    return 0


w = P.stream("w", step, fin, state=[("tau", NUM), ("hole", HOLE(LIST(WEDGE)))], elem=WEDGE)


def prog(d, tau, cands):
    val, hole = d.hole(LIST(WEDGE))
    r = d.call(w, list=cands, init=(tau, hole))
    d.erase(r)
    return val


P.prog("t5_decide_filter", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
