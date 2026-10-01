import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib.glue import Program, NUM, WEDGE

P = Program()

# Stream walker for counting
def step(d, tau, acc, u, v, score):
    # Erase u and v since we only care about the score
    d.erase(u, v)
    # Fanout tau since we need it in the next iteration
    tau1, tau2 = d.fanout(tau, 2)
    # Fanout acc since we need it in both branches of select
    acc1, acc2 = d.fanout(acc, 2)
    # Check if score >= tau: compute score < tau, then NOT it with "!" operator
    # (score < tau) ! 1 gives 1 if score >= tau (not-equal with 1 gives 1 iff the first operand is 0)
    lt = d.op(score, "<", tau1)
    ge = d.op(lt, "!", 1)
    # Conditionally increment accumulator: if ge then acc+1 else acc
    new_acc = d.select(ge, d.op(acc1, "+", 1), acc2)
    # Return new state (tau, acc)
    return (tau2, new_acc)

def fin(d, tau, acc):
    # At end, erase tau and return just the count
    d.erase(tau)
    return acc

w = P.stream("w", step, fin, state=[("tau", NUM), ("acc", NUM)], elem=WEDGE)

def prog(d, tau, cands):
    # Call the stream walker with initial state (tau, 0)
    return d.call(w, list=cands, init=(tau, 0))

P.prog("t5_decide_count", prog)
P.write(os.path.join(D, "net.hvm"))
