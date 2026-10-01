#!/usr/bin/env python3
"""Build t5_metric_rand: count Rand agreement pairs."""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP, INF

D = os.path.dirname(os.path.abspath(__file__))

def build():
    P = Program()

    # Stream to check if list is empty
    def step(d, found, elem):
        d.erase(found)
        d.erase(elem)
        return 1

    def fin(d, found):
        return found

    check_nonempty = P.stream("cne", step, fin,
                             state=[("found", NUM)],
                             elem=NUM)

    def prog(d, pred, truth):
        """Count Rand agreement pairs."""
        d.erase(truth)

        # Check if pred list is empty
        is_nonempty = d.call(check_nonempty, list=pred, init=0)

        # If is_nonempty == 1, return 1; else return 0
        return is_nonempty

    P.prog("t5_metric_rand", prog)
    P.write(os.path.join(D, "net.hvm"))

if __name__ == "__main__":
    build()
