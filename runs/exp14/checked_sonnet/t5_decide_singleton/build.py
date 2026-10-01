import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM

P = Program()


def step(d, tau, best, bi, i, x):
    x1, x2 = d.fanout(x, 2)
    best1, best2 = d.fanout(best, 2)
    i1, i2 = d.fanout(i, 2)
    gt = d.op(x1, ">", best1)
    g1, g2 = d.fanout(gt, 2)
    nbest = d.select(g1, x2, best2)
    nbi = d.select(g2, i1, bi)
    ni = d.op(i2, "+", 1)
    return tau, nbest, nbi, ni


def fin(d, tau, best, bi, i):
    d.erase(i)
    lt = d.op(tau, ">", best)
    return d.select(lt, 6, bi)


w = P.stream("w", step, fin,
             state=[("tau", NUM), ("best", NUM), ("bi", NUM), ("i", NUM)], elem=NUM)


def prog(d, tau, probs):
    return d.call(w, list=probs, init=(tau, 0, 0, 0))


P.prog("t5_decide_singleton", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
