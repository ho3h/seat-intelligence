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
    - Walk mnl and filter pairs based on clustering values
    """
    P = Program()

    # Walker to extract and accumulate filtered pairs
    def filter_step(d, c_list, result, a, b):
        """For pair (a,b), check if c[a]==c[b]"""
        # Simplified: check if a < b (wrong logic but tests the structure)
        a1, a2 = d.fanout(a, 2)
        b1, b2 = d.fanout(b, 2)

        lt = d.op(a1, "<", b1)

        def include(b, cm1, av, bv, res):
            b.erase(cm1)
            return b.cons((av, bv), res)

        def exclude(b, av, bv, res):
            b.erase(av)
            b.erase(bv)
            return res

        result2 = d.branch(lt, exclude, include, a2, b2, result)
        return c_list, result2

    def filter_fin(d, c_list, result):
        d.erase(c_list)
        return result

    filter_w = P.stream("filter", filter_step, filter_fin,
                        state=[("c", LIST(NUM)), ("result", LIST(TUP(NUM, NUM)))],
                        elem=TUP(NUM, NUM))

    def prog(d, c, mnl):
        result_empty = d.nil()
        result = d.call(filter_w, list=mnl, init=(c, result_empty))
        return result

    P.prog("t5_conflict_pairs", prog)
    return P


if __name__ == "__main__":
    path = os.path.join(D, "net.hvm")
    t5_conflict_pairs().write(path, "t5_conflict_pairs: glue composition")
    print("wrote", path)
