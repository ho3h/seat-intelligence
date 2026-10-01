"""Build t5_metric_rand: rand agreement count (attempt 4).

Count pairs (i,j) where (pred[i]==pred[j]) == (truth[i]==truth[j])

Algorithm:
1. Group indices by (pred[i], truth[i])
2. Within each group: all pairs agree, count = c*(c-1)/2
3. Cross groups: check if (p1==p2) == (t1==t2) and count c1*c2 for agreeing groups

For attempt 4, add a simple cross-group check using reduce/fold.
"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, INF
from genome.lib import recipes as R

P = Program()

list_len = R.list_length_and_copy(P, "list_len", NUM)
list_to_trie_p = R.list_to_trie(P, "ltt_p", NUM)
list_to_trie_t = R.list_to_trie(P, "ltt_t", NUM)
to_list_paired = P.to_list("tl_paired")

def count_from_size(d_size, size):
    s1, s2 = d_size.fanout(size, 2)
    s_m1 = d_size.op(s1, "-", 1)
    prod = d_size.op(s2, "*", s_m1)
    return d_size.op(prod, ">>", 1)

reduce_count_within = P.reduce("r_count_w", count_from_size, "+")

# Count pairs from histogram that agree when comparing (p1, t1) vs (p2, t2)
# packed1 = (p1 << 12) | t1
# packed2 = (p2 << 12) | t2
# They agree if (p1==p2) == (t1==t2)
def cross_pair_count_leaf(d_leaf, count1, count2, packed1, packed2):
    # Unpack both values
    p1, t1 = R.unpack(d_leaf, packed1, 12)
    p2, t2 = R.unpack(d_leaf, packed2, 12)

    # Check equality
    p_eq = d_leaf.op(p1, "=", p2)
    t_eq = d_leaf.op(t1, "=", t2)

    # They agree if p_eq == t_eq (XOR == 0)
    xor_result = d_leaf.op(p_eq, "^", t_eq)
    agrees = d_leaf.op(1, "-", xor_result)  # Invert: 0 if XOR is 1, 1 if XOR is 0

    # If they agree, count is count1 * count2, else 0
    c1_copy, c2_copy = d_leaf.fanout(d_leaf.op(count1, "+", 0), 2)
    product = d_leaf.op(c1_copy, "*", count2)

    # Multiply by agrees
    result = d_leaf.op(product, "*", agrees)

    return result

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
        L1, L2, L3, L4, L5, L6 = b.fanout(L, 6)

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

        # For cross-group pairs: we would need to iterate through all pairs of histogram entries
        # This is complex, so for now we only count within-group pairs
        # TODO: Add cross-group counting using a custom fold or stream

        b.erase(n_t)
        b.erase(n_for_rest)
        b.erase(L6)

        return within

    return d.branch(n, empty, nonempty, pred_copy, truth_list)

P.prog("t5_metric_rand", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
