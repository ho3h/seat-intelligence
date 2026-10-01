import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, WEDGE

P = Program()


def step(d, tau, cnt, u, v, s):
    d.erase(u, v)
    tau1, tau2 = d.fanout(tau, 2)
    lt = d.op(s, "<", tau1)          # 1 if score < tau
    ge = d.op(1, "-", lt)            # 1 if score >= tau
    cnt2 = d.op(cnt, "+", ge)
    return tau2, cnt2


def fin(d, tau, cnt):
    d.erase(tau)
    return cnt


w = P.stream("w", step, fin, state=[("tau", NUM), ("cnt", NUM)], elem=WEDGE)


def prog(d, tau, cands):
    return d.call(w, list=cands, init=(tau, 0))


P.prog("t5_decide_count", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
