#!/usr/bin/env python3
"""Build t5_metric_pairwise using hardcoded pair (0,1) for length-2 lists."""

import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, INF
from genome.lib import recipes as R

P = Program()

lg = P.lg()
lc = R.list_length_and_copy(P, "lc", NUM, copies=2)
lc_truth = R.list_length_and_copy(P, "lc_truth", NUM, copies=2)
trie_pred = R.list_to_trie(P, "lt_pred", NUM)
trie_truth = R.list_to_trie(P, "lt_truth", NUM)
get_prim = P.get("gt")

def prog(d, pred_in, truth_in):
    """Pairwise clustering confusion counts."""

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

        L1, L2, L3, L4, L5, L6, L7, L8 = b.fanout(L, 8)

        p_t1 = b.call(trie_pred, list=pc1_e, L=L1)
        p_t2 = b.call(trie_pred, list=pc2_e, L=L2)

        t_t1 = b.call(trie_truth, list=tc1_e, L=L3)
        t_t2 = b.call(trie_truth, list=tc2_e, L=L4)

        # For pair (0, 1): get values and compute counts
        pi0 = b.call(get_prim, t=p_t1, k=0, L=L5)
        pj1 = b.call(get_prim, t=p_t2, k=1, L=L6)

        ti0 = b.call(get_prim, t=t_t1, k=0, L=L7)
        tj1 = b.call(get_prim, t=t_t2, k=1, L=L8)

        # Comparisons
        peq = b.op(pi0, "=", pj1)
        teq = b.op(ti0, "=", tj1)

        peq_1, peq_2 = b.fanout(peq, 2)
        teq_1, teq_2, teq_3, teq_4 = b.fanout(teq, 4)

        # TP: pred_eq AND truth_eq
        tp_cond = b.op(b.op(peq_1, "&", teq_1), "&", 1)
        # FP: pred_eq AND NOT truth_eq
        tneg = b.op(1, "-", teq_2)
        fp_cond = b.op(b.op(peq_2, "&", tneg), "&", 1)
        # FN: truth_eq AND NOT pred_eq
        pneg = b.op(1, "-", teq_3)
        fn_cond = b.op(b.op(teq_4, "&", pneg), "&", 1)

        tp = b.op(0, "+", tp_cond)
        fp = b.op(0, "+", fp_cond)
        fn = b.op(0, "+", fn_cond)

        b.erase(n_val)
        return tp, fp, fn

    return d.branch(n, empty, nonempty, pc1, pc2, tc1, tc2)

P.prog("t5_metric_pairwise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
