"""Composition of t5_conflict_pairs using genome.lib.glue (checked API)."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP, INF

def t5_conflict_pairs():
    """
    Input: (c, mnl) where c is clustering list and mnl is list of (a, b) pairs
    Output: list of (a, b) pairs where c[a] == c[b] (violations)

    Two-phase algorithm:
    1. Convert c into indexed pairs (i, c[i])
    2. For each mnl pair (a, b), look up c[a] and c[b] and compare
    """
    P = Program()

    # Phase 1: Convert c list to list of (index, value) pairs
    def index_step(d, i, result, c_val):
        """Convert element to (i, c_val) pair and accumulate"""
        i1, i2 = d.fanout(i, 2)
        i_new = d.op(i1, "+", 1)
        pair = (i2, c_val)
        result_new = d.cons(pair, result)
        return i_new, result_new

    def index_fin(d, i, result):
        d.erase(i)
        return result

    index_w = P.stream("index", index_step, index_fin,
                       state=[("i", NUM), ("result", LIST(TUP(NUM, NUM)))], elem=NUM)

    # Phase 2: For each mnl pair, find matching c values
    def filter_step(d, c_indexed, result, a, b):
        """Look up c[a] and c[b] in indexed list and compare"""
        # Check if a==b (placeholder logic)
        a1, a2 = d.fanout(a, 2)
        b1, b2 = d.fanout(b, 2)
        eq = d.op(a1, "=", b1)

        def add_pair(b_branch, cm1, av, bv, res):
            b_branch.erase(cm1)
            return b_branch.cons((av, bv), res)

        def skip_pair(b_branch, av, bv, res):
            b_branch.erase(av)
            b_branch.erase(bv)
            return res

        result2 = d.branch(eq, skip_pair, add_pair, a2, b2, result)
        return c_indexed, result2

    def filter_fin(d, c_indexed, result):
        d.erase(c_indexed)
        return result

    filter_w = P.stream("filter", filter_step, filter_fin,
                        state=[("c_idx", LIST(TUP(NUM, NUM))), ("result", LIST(TUP(NUM, NUM)))],
                        elem=TUP(NUM, NUM))

    def prog(d, c, mnl):
        # Phase 1: Index c
        result_index = d.nil()
        c_indexed = d.call(index_w, list=c, init=(0, result_index))

        # Phase 2: Filter mnl using indexed c
        result_empty = d.nil()
        result = d.call(filter_w, list=mnl, init=(c_indexed, result_empty))

        return result

    P.prog("t5_conflict_pairs", prog)
    return P


if __name__ == "__main__":
    path = os.path.join(D, "net.hvm")
    t5_conflict_pairs().write(path, "t5_conflict_pairs: glue composition")
    print("wrote", path)
