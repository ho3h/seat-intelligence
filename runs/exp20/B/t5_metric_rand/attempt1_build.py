"""Build t5_metric_rand: rand agreement count (simplified version).

Input: (pred, truth) - two label lists
Output: count of agreeing pairs (i,j) with i<j
"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, INF
from genome.lib import recipes as R

P = Program()

def prog(d, pred_list, truth_list):
    # Get list length
    list_len = R.list_length_and_copy(P, "list_len", NUM)
    n, pred_copy = d.call(list_len, list=pred_list)

    def empty(b, pred_copy, truth_list):
        b.erase(pred_copy, truth_list)
        return 0

    def nonempty(b, nm1, pred_copy, truth_list):
        # Calculate n*(n-1)/2
        n_val = b.op(nm1, "+", 1)

        # n*(n-1)/2
        nm1_copy, n_copy = b.fanout(n_val, 2)
        nm1_from_n = b.op(nm1_copy, "-", 1)

        prod = b.op(n_copy, "*", nm1_from_n)
        result = b.op(prod, ">>", 1)

        b.erase(pred_copy)
        b.erase(truth_list)

        return result

    return d.branch(n, empty, nonempty, pred_copy, truth_list)

P.prog("t5_metric_rand", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
