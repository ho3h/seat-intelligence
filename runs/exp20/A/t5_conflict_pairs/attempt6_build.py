"""Composition of t5_conflict_pairs using genome.lib.glue (checked API)."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP, INF

def t5_conflict_pairs():
    P = Program()

    def filter_step(d, result, a, b):
        """Add all pairs to result"""
        return d.cons((a, b), result)

    def filter_fin(d, result):
        return result

    filter_w = P.stream("filter", filter_step, filter_fin,
                        state=[("result", LIST(TUP(NUM, NUM)))],
                        elem=TUP(NUM, NUM))

    def prog(d, c, mnl):
        d.erase(c)
        return d.call(filter_w, list=mnl, init=d.nil())

    P.prog("t5_conflict_pairs", prog)
    return P


if __name__ == "__main__":
    path = os.path.join(D, "net.hvm")
    t5_conflict_pairs().write(path, "t5_conflict_pairs: glue composition")
    print("wrote", path)
