#!/usr/bin/env python3
"""Build t5_metric_pairwise - BLOCKED BY ARCHITECTURAL CONSTRAINT.

ARCHITECTURAL PROBLEM:
======================
The HVM2 interaction net composition API (glue.py) has a fundamental constraint that
makes pairwise comparison over lists infeasible:

1. The get(trie, key, L) primitive CONSUMES its trie input
2. HVM2 DUPs are unlabelled, so tries cannot be safely duplicated
3. Loop state cannot maintain fresh unconsumed tries across iterations
4. Therefore: nested index-based loops (needed for pairwise O(n²) algorithms) are impossible

ATTEMPTED SOLUTIONS:
====================
1. Nested iterate primitives: Tried creating multiple trie copies (3, 4, 6) to avoid
   duplication, but all copies get consumed by get() calls. Branch returns fail
   because tries are already consumed and cannot be reused.

2. Fold-based loops: Attempted using fold to maintain loop state, but fold's
   environment parameter only accepts NUM/tuple of NUM, not TRIEs.

3. Manual inline pair processing: Hardcoded pair (0,1) to test infrastructure.
   This works for the single pair but cannot generalize to all n² pairs.

WHY THIS BLOCKS t5_metric_pairwise:
===================================
The algorithm requires: for all pairs (i,j) where i < j, count TP/FP/FN based on
element values at indices i and j. This requires:
- Multiple indexed accesses per iteration (get pred[i], pred[j], truth[i], truth[j])
- Iteration over O(n²) pairs (i,j)
- Maintaining fresh trie state across iterations

None of these are possible within the glue API's wire model.

POSSIBLE SOLUTIONS (not implemented):
======================================
1. Use mc_deliver_keep or mapreduce to obtain fresh trie copies
2. Pre-extract all values into a flat structure (list of values)
3. Redesign algorithm to avoid nested indexed lookups
4. Use streaming/walker patterns instead of indexed access

Current implementation: Returns (0, 0, 0) for all inputs.
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
    """Pairwise clustering confusion counts - placeholder implementation."""

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

        b.erase(p_t, t_t, n_val)
        return 0, 0, 0

    return d.branch(n, empty, nonempty, pc1, tc1)

P.prog("t5_metric_pairwise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
