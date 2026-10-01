#!/usr/bin/env python3
"""Build t5_metric_pairwise: pairwise clustering confusion counts."""

import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, INF
from genome.lib import recipes as R

P = Program()

lg = P.lg()
lc = R.list_length_and_copy(P, "lc", NUM, copies=2)
lc_truth = R.list_length_and_copy(P, "lc_truth", NUM, copies=2)
trie_pred = R.list_to_trie(P, "lt_pred", NUM)
trie_truth = R.list_to_trie(P, "lt_truth", NUM)

def prog(d, pred_in, truth_in):
    """
    Input: (pred, truth) - two lists of u24
    Output: (tp, fp, fn) - tuple of three u24 values

    Algorithm: For all pairs (i,j) where i < j:
    - TP: pred[i]==pred[j] AND truth[i]==truth[j]
    - FP: pred[i]==pred[j] AND truth[i]!=truth[j]
    - FN: truth[i]==truth[j] AND pred[i]!=pred[j]
    """

    n, pc1, pc2 = d.call(lc, list=pred_in)
    n2, tc1, tc2 = d.call(lc_truth, list=truth_in)
    d.erase(n2)

    def empty(b, pc1_e, pc2_e, tc1_e, tc2_e):
        b.erase(pc1_e, pc2_e, tc1_e, tc2_e)
        return 0, 0, 0

    def nonempty(b, nm1, pc1_e, pc2_e, tc1_e, tc2_e):
        nm1_a, nm1_b = b.fanout(nm1, 2)
        n_val = b.op(nm1_a, "+", 1)
        L = b.call(lg, x=nm1_b)

        L1, L2, L3, L4 = b.fanout(L, 4)

        p_t1 = b.call(trie_pred, list=pc1_e, L=L1)
        p_t2 = b.call(trie_pred, list=pc2_e, L=L2)

        t_t1 = b.call(trie_truth, list=tc1_e, L=L3)
        t_t2 = b.call(trie_truth, list=tc2_e, L=L4)

        # For now, return (0, 0, 0) as a placeholder
        # TODO: implement pairwise comparison logic
        b.erase(p_t1, p_t2, t_t1, t_t2, n_val)
        return 0, 0, 0

    return d.branch(n, empty, nonempty, pc1, pc2, tc1, tc2)

P.prog("t5_metric_pairwise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
