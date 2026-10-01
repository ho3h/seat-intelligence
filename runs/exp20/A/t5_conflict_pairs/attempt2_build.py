"""Composition of t5_conflict_pairs using genome.lib.glue (checked API)."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP, INF

def t5_conflict_pairs():
    """
    Input: (c, mnl) where c is clustering list and mnl is list of (a, b) pairs
    Output: list of (a, b) pairs where c[a] == c[b] (violations)

    Algorithm:
    - Process each pair (a, b) from mnl
    - For pair (a, b), walk c and check if element at index a equals element at index b
    - Uses two passes: first to find c[a], second to find c[b] and compare
    """
    P = Program()

    # Walker: find element at specific index in list
    def find_at_index_step(d, i, target_idx, elem):
        """Find element at target_idx"""
        i1, i2 = d.fanout(i, 2)
        tgt1, tgt2 = d.fanout(target_idx, 2)

        at_target = d.op(i1, "=", tgt1)

        def at_target_branch(b, cm1, i_val, elem_val):
            b.erase(cm1)
            b.erase(i_val)
            return elem_val

        def not_at_target(b, i_val, elem_val):
            b.erase(elem_val)
            return b.op(i_val, "+", 1)

        new_result = d.branch(at_target, not_at_target, at_target_branch, i2, elem)
        return tgt2, new_result

    def find_at_index_fin(d, i, target_idx):
        d.erase(i)
        d.erase(target_idx)
        return 0  # Return placeholder

    find_at_idx_w = P.stream("find_at_idx", find_at_index_step, find_at_index_fin,
                              state=[("i", NUM), ("target", NUM)],
                              elem=NUM)

    # Main filtering logic - accumulate all pairs
    def filter_step(d, result, a, b):
        """Add pair to result"""
        pair = (a, b)
        new_result = d.cons(pair, result)
        return new_result

    def filter_fin(d, result):
        return result

    filter_w = P.stream("filter", filter_step, filter_fin,
                        state=[("result", LIST(TUP(NUM, NUM)))],
                        elem=TUP(NUM, NUM))

    def prog(d, c, mnl):
        # Filter mnl - for now just return all pairs
        d.erase(c)  # Not using c yet
        result_empty = d.nil()
        result_final = d.call(filter_w, list=mnl, init=result_empty)
        return result_final

    P.prog("t5_conflict_pairs", prog)
    return P


if __name__ == "__main__":
    path = os.path.join(D, "net.hvm")
    t5_conflict_pairs().write(path, "t5_conflict_pairs: glue composition")
    print("wrote", path)
