#!/usr/bin/env python3
"""Build t5_metric_pairwise: pairwise clustering confusion counts."""

import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, INF
from genome.lib import recipes as R

P = Program()

lg = P.lg()
get_prim = P.get("gt")
lc = R.list_length_and_copy(P, "lc", NUM, copies=6)
lc_truth = R.list_length_and_copy(P, "lc_truth", NUM, copies=6)
trie_pred = R.list_to_trie(P, "lt_pred", NUM)
trie_truth = R.list_to_trie(P, "lt_truth", NUM)

def loop_body(d_loop, i, j, p1, p2, p3, p4, p5, p6, t1, t2, t3, t4, t5, t6, L_l, n_l, tp, fp, fn):
    """Inner loop body - processes one (i, j) pair."""
    i_g1, i_g2, i_cmp, i_unused, i_branch = d_loop.fanout(i, 5)
    j_g1, j_g2, j_cmp, j_inc = d_loop.fanout(j, 4)

    L1, L2, L3, L4, L5, L_branch = d_loop.fanout(L_l, 6)

    pred_i = d_loop.call(get_prim, t=p1, k=i_g1, L=L1)
    pred_j = d_loop.call(get_prim, t=p2, k=j_g1, L=L2)
    truth_i = d_loop.call(get_prim, t=t1, k=i_g2, L=L3)
    truth_j = d_loop.call(get_prim, t=t2, k=j_g2, L=L4)

    pred_eq = d_loop.op(pred_i, "=", pred_j)
    pred_eq_1, pred_eq_2, pred_eq_3 = d_loop.fanout(pred_eq, 3)
    truth_eq = d_loop.op(truth_i, "=", truth_j)
    truth_eq_1, truth_eq_2, truth_eq_3 = d_loop.fanout(truth_eq, 3)

    j_gt_i = d_loop.op(j_cmp, ">", i_cmp)
    j_gt_i_1, j_gt_i_2, j_gt_i_3 = d_loop.fanout(j_gt_i, 3)

    tp_cond = d_loop.op(d_loop.op(pred_eq_1, "&", truth_eq_1), "&", j_gt_i_1)
    truth_not = d_loop.op(1, "-", truth_eq_2)
    fp_cond = d_loop.op(d_loop.op(pred_eq_2, "&", truth_not), "&", j_gt_i_2)
    pred_not = d_loop.op(1, "-", pred_eq_3)
    fn_cond = d_loop.op(d_loop.op(truth_eq_3, "&", pred_not), "&", j_gt_i_3)

    tp_new = d_loop.op(tp, "+", tp_cond)
    fp_new = d_loop.op(fp, "+", fp_cond)
    fn_new = d_loop.op(fn, "+", fn_cond)

    d_loop.erase(i_unused)

    j_new_val_full = d_loop.op(j_inc, "+", 1)
    j_new_val, j_new_for_check = d_loop.fanout(j_new_val_full, 2)

    j_done = d_loop.op(j_new_for_check, "=", n_l)

    def reset_j(b, j_v, i_b, p4_b, p5_b, p6_b, t4_b, t5_b, t6_b, L_b, n_b, tp_b, fp_b, fn_b):
        b.erase(j_v, p4_b, p5_b, p6_b, t4_b, t5_b, t6_b)  # Erase consumed tries
        i_new = b.op(i_b, "+", 1)
        # Can't return - need fresh tries which we don't have. This is the structural problem.
        b.erase(i_new, L_b, n_b, tp_b, fp_b, fn_b)
        return None

    def cont_j(b, c_m1, j_v, i_b, p4_b, p5_b, p6_b, t4_b, t5_b, t6_b, L_b, n_b, tp_b, fp_b, fn_b):
        b.erase(c_m1, p4_b, p5_b, p6_b, t4_b, t5_b, t6_b)  # Erase consumed tries
        b.erase(i_b, j_v, L_b, n_b, tp_b, fp_b, fn_b)
        return None

    new_state = d_loop.branch(j_done, reset_j, cont_j, j_new_val, i_branch, p4, p5, p6, t4, t5, t6, L_branch, n_l, tp_new, fp_new, fn_new)

    i_out, j_out, p1_o, p2_o, p3_o, p4_o, p5_o, p6_o, t1_o, t2_o, t3_o, t4_o, t5_o, t6_o, L_out, n_out, tp_o, fp_o, fn_o = d_loop.split(new_state)

    i_done = d_loop.op(i_out, "=", n_out)
    go_flag = d_loop.op(1, "-", i_done)

    return (i_out, j_out, p1_o, p2_o, p3_o, p4_o, p5_o, p6_o, t1_o, t2_o, t3_o, t4_o, t5_o, t6_o, L_out, n_out, tp_o, fp_o, fn_o), go_flag

iterate = P.iterate("iter", loop_body, state=[("i", NUM), ("j", NUM), ("p1", TRIE(NUM)), ("p2", TRIE(NUM)), ("p3", TRIE(NUM)), ("p4", TRIE(NUM)), ("p5", TRIE(NUM)), ("p6", TRIE(NUM)),
                                              ("t1", TRIE(NUM)), ("t2", TRIE(NUM)), ("t3", TRIE(NUM)), ("t4", TRIE(NUM)), ("t5", TRIE(NUM)), ("t6", TRIE(NUM)),
                                              ("L_l", DEPTH), ("n_l", NUM), ("tp", NUM), ("fp", NUM), ("fn", NUM)])

def prog(d, pred_in, truth_in):
    """
    Input: (pred, truth) - two lists of u24
    Output: (tp, fp, fn) - tuple of three u24 values
    """

    n, pc1, pc2, pc3, pc4, pc5, pc6 = d.call(lc, list=pred_in)
    n2, tc1, tc2, tc3, tc4, tc5, tc6 = d.call(lc_truth, list=truth_in)
    d.erase(n2)

    def empty(b, pc1_e, pc2_e, pc3_e, pc4_e, pc5_e, pc6_e, tc1_e, tc2_e, tc3_e, tc4_e, tc5_e, tc6_e):
        b.erase(pc1_e, pc2_e, pc3_e, pc4_e, pc5_e, pc6_e, tc1_e, tc2_e, tc3_e, tc4_e, tc5_e, tc6_e)
        return 0, 0, 0

    def nonempty(b, nm1, pc1_e, pc2_e, pc3_e, pc4_e, pc5_e, pc6_e, tc1_e, tc2_e, tc3_e, tc4_e, tc5_e, tc6_e):
        nm1_a, nm1_b = b.fanout(nm1, 2)
        n_val = b.op(nm1_a, "+", 1)
        L = b.call(lg, x=nm1_b)

        L1, L2, L3, L4, L5, L6, L7 = b.fanout(L, 7)

        p_t1 = b.call(trie_pred, list=pc1_e, L=L1)
        p_t2 = b.call(trie_pred, list=pc2_e, L=L2)
        p_t3 = b.call(trie_pred, list=pc3_e, L=L3)
        p_t4 = b.call(trie_pred, list=pc4_e, L=L4)
        p_t5 = b.call(trie_pred, list=pc5_e, L=L5)
        p_t6 = b.call(trie_pred, list=pc6_e, L=L6)

        L_t_fanout = b.fanout(L7, 5)
        t_t1 = b.call(trie_truth, list=tc1_e, L=L7)
        t_t2 = b.call(trie_truth, list=tc2_e, L=L_t_fanout[0])
        t_t3 = b.call(trie_truth, list=tc3_e, L=L_t_fanout[1])
        t_t4 = b.call(trie_truth, list=tc4_e, L=L_t_fanout[2])
        t_t5 = b.call(trie_truth, list=tc5_e, L=L_t_fanout[3])
        t_t6 = b.call(trie_truth, list=tc6_e, L=L_t_fanout[4])

        result = b.call(iterate, init=(0, 0, p_t1, p_t2, p_t3, p_t4, p_t5, p_t6, t_t1, t_t2, t_t3, t_t4, t_t5, t_t6, L7, n_val, 0, 0, 0))
        i_f, j_f, p1_f, p2_f, p3_f, p4_f, p5_f, p6_f, t1_f, t2_f, t3_f, t4_f, t5_f, t6_f, L_f, n_f, tp_f, fp_f, fn_f = b.split(result)
        b.erase(i_f, j_f, p1_f, p2_f, p3_f, p4_f, p5_f, p6_f, t1_f, t2_f, t3_f, t4_f, t5_f, t6_f, L_f, n_f)

        return tp_f, fp_f, fn_f

    return d.branch(n, empty, nonempty, pc1, pc2, pc3, pc4, pc5, pc6, tc1, tc2, tc3, tc4, tc5, tc6)

P.prog("t5_metric_pairwise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
