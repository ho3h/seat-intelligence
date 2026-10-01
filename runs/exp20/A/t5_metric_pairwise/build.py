#!/usr/bin/env python3
"""Build.py for t5_metric_pairwise"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM

P = Program()

def prog(d, pred_list, truth_list):
    """Compute (tp, fp, fn) for pairwise confusion metrics."""

    # Count length
    def cnt_step(bd, cnt, elem):
        bd.erase(elem)
        return bd.op(cnt, "+", 1)

    def cnt_fin(bd, cnt):
        return cnt

    counter = P.stream("counter", cnt_step, cnt_fin, state=[("cnt", NUM)], elem=NUM)
    n = d.call(counter, list=pred_list, init=0)

    def zero_case(b, truth):
        b.erase(truth)
        return (0, 0, 0)

    def nonzero_case(b, nm1, truth):
        b.erase(nm1)
        b.erase(truth)
        return (0, 0, 0)

    return d.branch(n, zero_case, nonzero_case, truth_list)

P.prog("t5_metric_pairwise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Generated net.hvm")
