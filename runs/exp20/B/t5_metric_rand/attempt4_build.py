"""Build t5_metric_rand: rand agreement count (attempt 3).

Fix: use R.depth_for instead of lg(n-1) for proper depth calculation.
"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, INF
from genome.lib import recipes as R

P = Program()

list_len = R.list_length_and_copy(P, "list_len", NUM)
list_to_trie_p = R.list_to_trie(P, "ltt_p", NUM)
list_to_trie_t = R.list_to_trie(P, "ltt_t", NUM)
lg_inst = P.lg()
to_list_paired = P.to_list("tl_paired")

def count_from_size(d_size, size):
    s1, s2 = d_size.fanout(size, 2)
    s_m1 = d_size.op(s1, "-", 1)
    prod = d_size.op(s2, "*", s_m1)
    return d_size.op(prod, ">>", 1)

reduce_count_within = P.reduce("r_count_w", count_from_size, "+")

def prog(d, pred_list, truth_list):
    n, pred_copy = d.call(list_len, list=pred_list)

    def empty(b, pred_copy, truth_list):
        b.erase(pred_copy, truth_list)
        return 0

    def nonempty(b, nm1, pred_copy, truth_list):
        n_val = b.op(nm1, "+", 1)
        n_for_trie, n_for_list, n_for_rest = b.fanout(n_val, 3)

        # Use depth_for for proper depth calculation
        L = R.depth_for(P, b, n_for_trie)
        L1, L2, L3, L4, L5 = b.fanout(L, 5)

        pred_trie = b.call(list_to_trie_p, list=pred_copy, L=L1)

        list_len_t = R.list_length_and_copy(P, "list_len_t", NUM)
        n_t, truth_copy = b.call(list_len_t, list=truth_list)

        truth_trie = b.call(list_to_trie_t, list=truth_copy, L=L2)

        # Combine pred and truth tries using zip2
        def zip_leaf(d_zip, p, t):
            return R.pack(d_zip, p, t, 12)

        zip_trie = P.zip2("z2_pt", zip_leaf)

        L3_1, L3_2 = b.fanout(L3, 2)
        paired_trie = b.call(zip_trie, a=pred_trie, c=truth_trie, L=L3_1)

        # Convert paired trie to list
        paired_list = b.call(to_list_paired, t=paired_trie, L=L3_2, n=n_for_list)

        # Group by packed value
        def keyval(d_key, packed):
            return packed, 1

        rbk = R.reduce_by_key(P, "rbk", NUM, keyval, combine="add")

        histogram = b.call(rbk, list=paired_list, L=L4)

        # Count within-group pairs
        within = b.call(reduce_count_within, t=histogram, L=L5)

        b.erase(n_t)
        b.erase(n_for_rest)

        return within

    return d.branch(n, empty, nonempty, pred_copy, truth_list)

P.prog("t5_metric_rand", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
