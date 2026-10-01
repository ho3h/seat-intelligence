#!/usr/bin/env python3
"""Build HVM net for t5_decide_singleton using simple stream walker."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(D)))

from genome.lib.glue import Program, NUM

P = Program()

def step(d, idx, max_val, min_idx, val):
    """Process one element: update max and its lowest index."""
    # Compute next index
    next_idx = d.op(idx, "+", 1)

    # Compare val with max_val using select
    gt = d.op(val, ">", max_val)

    # Use branch
    def if_greater(b, _):
        b.erase(_)
        return next_idx, val, idx

    def if_not_greater(b):
        # Also check equality and index
        eq = b.op(val, "=", max_val)

        def if_equal(b2, _):
            b2.erase(_)
            # Check if current idx is lower
            lt = b2.op(idx, "<", min_idx)

            def if_lower(b3, _):
                b3.erase(_)
                return next_idx, max_val, idx

            def if_not_lower(b3):
                return next_idx, max_val, min_idx

            return b2.branch(lt, if_lower, if_not_lower)

        def if_not_equal(b2):
            return next_idx, max_val, min_idx

        return b.branch(eq, if_equal, if_not_equal)

    return d.branch(gt, if_not_greater, if_greater)

def fin(d, idx, max_val, min_idx):
    d.erase(idx)
    return d.op(d.op(max_val, "<<", 3), "|", min_idx)

w = P.stream("w", step, fin,
             state=[("idx", NUM), ("max_val", NUM), ("min_idx", NUM)],
             elem=NUM)

def prog(d, tau, probs):
    packed = d.call(w, list=probs, init=(0, 0, 0))

    p1, p2 = d.fanout(packed, 2)
    max_val = d.op(p1, ">>", 3)
    min_idx = d.op(p2, "&", 7)

    is_below = d.op(tau, ">", max_val)

    def abstain(b, mi):
        b.erase(mi)
        return 6

    def return_min(b, _, mi):
        b.erase(_)
        return mi

    return d.branch(is_below, abstain, return_min, min_idx)

P.prog("t5_decide_singleton", prog)
P.write(os.path.join(D, "net.hvm"))
print(f"Wrote net.hvm")
