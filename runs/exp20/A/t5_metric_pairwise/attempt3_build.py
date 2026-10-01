#!/usr/bin/env python3
"""Build.py for t5_metric_pairwise"""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM

P = Program()

def prog(d, pred_list, truth_list):
    """Compute (tp, fp, fn) for pairwise confusion metrics."""

    # Count list length using stream
    def count_step(bd, cnt, elem):
        bd.erase(elem)
        return bd.op(cnt, "+", 1)

    def count_fin(bd, cnt):
        return cnt

    len_walker = P.stream("len_walker", count_step, count_fin, state=[("cnt", NUM)], elem=NUM)
    n = d.call(len_walker, list=pred_list, init=0)

    # Simple branching based on n
    def handle_zero(b, truth):
        b.erase(truth)
        return (0, 0, 0)

    def handle_nonzero(b, nm1, truth):
        # For now, return (0, 0, 0)
        # TODO: implement full algorithm
        b.erase(nm1)
        b.erase(truth)
        return (0, 0, 0)

    return d.branch(n, handle_zero, handle_nonzero, truth_list)

P.prog("t5_metric_pairwise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Generated net.hvm")
