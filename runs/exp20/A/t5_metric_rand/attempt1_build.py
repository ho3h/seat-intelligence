#!/usr/bin/env python3
"""Build t5_metric_rand: count Rand agreement pairs."""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP, INF

D = os.path.dirname(os.path.abspath(__file__))

def build():
    P = Program()

    # Primitives
    lg = P.lg()
    const_zero = P.const_trie("z0", 0)
    hadd = P.update("hadd", "add")
    reduce_sum = P.reduce("rsum", lambda d, x: x, "+")

    # Simple walker to process a single list and build a trie
    def step(d2, cnt, trie, elem):
        # cnt: current index (implicit counter)
        # trie: accumulating trie of values
        # elem: current element value
        # For now, just pass through, erasing element
        d2.erase(elem)
        return (cnt, trie)

    def fin(d2, cnt, trie):
        # Return just the trie (ignore cnt for now)
        d2.erase(cnt)
        return trie

    walker = P.stream("walk", step, fin,
                     state=[("cnt", NUM), ("trie", TRIE(NUM))],
                     elem=NUM)

    def prog(d, pred, truth):
        """Count Rand agreement pairs."""

        # Compute depth for trie
        lg_val = d.call(lg, x=15)

        # Initialize trie
        trie_init = d.call(const_zero, L=lg_val)

        # Process pred list to build pred_trie
        pred_trie = d.call(walker, list=pred, init=(0, trie_init))

        # For now, just return 0
        d.erase(pred_trie)
        d.erase(truth)
        return 0

    P.prog("t5_metric_rand", prog)
    P.write(os.path.join(D, "net.hvm"))

if __name__ == "__main__":
    build()
