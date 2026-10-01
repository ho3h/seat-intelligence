#!/usr/bin/env python3
"""Build t5_metric_rand: count Rand agreement pairs."""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP, INF

D = os.path.dirname(os.path.abspath(__file__))

def build():
    P = Program()

    def prog(d, pred, truth):
        """Count Rand agreement pairs - placeholder."""
        d.erase(pred)
        d.erase(truth)
        return 1  # Return 1 for now

    P.prog("t5_metric_rand", prog)
    P.write(os.path.join(D, "net.hvm"))

if __name__ == "__main__":
    build()
