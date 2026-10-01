#!/usr/bin/env python3
"""Build.py for t5_metric_pairwise"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, LIST, TUP

P = Program()

lg = P.lg()
z0 = P.const_trie("z0", 0)

def prog(d, pred_list, truth_list):
    """
    Compute (tp, fp, fn) for pairwise confusion metrics.

    Simple algorithm:
    1. Count n from pred_list
    2. Process all pairs (i,j) with i<j
    3. Count tp, fp, fn based on pred[i]==pred[j] and truth[i]==truth[j]
    """

    # Count list length using stream
    def count_step(bd, cnt, elem):
        bd.erase(elem)
        return bd.op(cnt, "+", 1)

    def count_fin(bd, cnt):
        return cnt

    len_walker = P.stream("len_walker", count_step, count_fin, state=[("cnt", NUM)], elem=NUM)
    n = d.call(len_walker, list=pred_list, init=0)

    # Check if n == 0
    def handle_empty(b, truth):
        b.erase(truth)
        return (0, 0, 0)

    def handle_nonempty(b, n_minus_1, truth):
        n = b.op(n_minus_1, "+", 1)

        # For now, return placeholder
        b.erase(n)
        b.erase(truth)
        return (0, 0, 0)

    return d.branch(n, handle_empty, handle_nonempty, truth_list)

P.prog("t5_metric_pairwise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Generated net.hvm")
