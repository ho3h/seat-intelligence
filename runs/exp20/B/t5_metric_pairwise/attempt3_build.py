#!/usr/bin/env python3
"""Build t5_metric_pairwise: pairwise clustering confusion counts.

ARCHITECTURAL CONSTRAINT: HVM2 tries consumed by get() cannot be reused or safely
duplicated (HVM2 DUPs are unlabelled). This blocks nested-loop algorithms that need
multiple indexed accesses per iteration. A proper solution requires:
1. Reconsidering the algorithm to avoid nested index lookups, OR
2. Using mc_deliver_keep or mapreduce to obtain fresh trie copies, OR
3. Pre-extracting all values into a different data structure

For now: returning placeholder (0, 0, 0) to validate test infrastructure.
"""

import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, INF
from genome.lib import recipes as R

P = Program()

lg = P.lg()
lc = R.list_length_and_copy(P, "lc", NUM, copies=1)
lc_truth = R.list_length_and_copy(P, "lc_truth", NUM, copies=1)
trie_pred = R.list_to_trie(P, "lt_pred", NUM)
trie_truth = R.list_to_trie(P, "lt_truth", NUM)

def prog(d, pred_in, truth_in):
    """
    Input: (pred, truth) - two lists of u24
    Output: (tp, fp, fn) - tuple of three u24 values
    """

    n, pc1 = d.call(lc, list=pred_in)
    n2, tc1 = d.call(lc_truth, list=truth_in)
    d.erase(n2)

    def empty(b, pc1_e, tc1_e):
        b.erase(pc1_e, tc1_e)
        return 0, 0, 0

    def nonempty(b, nm1, pc1_e, tc1_e):
        nm1_a, nm1_b = b.fanout(nm1, 2)
        n_val = b.op(nm1_a, "+", 1)
        L = b.call(lg, x=nm1_b)

        L1, L2 = b.fanout(L, 2)

        p_t = b.call(trie_pred, list=pc1_e, L=L1)
        t_t = b.call(trie_truth, list=tc1_e, L=L2)

        # TODO: Implement pairwise comparison logic
        # Currently blocked by architectural constraint: tries are consumed by get()
        # and cannot be reused or safely duplicated within nested loops
        b.erase(p_t, t_t, n_val)
        return 0, 0, 0

    return d.branch(n, empty, nonempty, pc1, tc1)

P.prog("t5_metric_pairwise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
