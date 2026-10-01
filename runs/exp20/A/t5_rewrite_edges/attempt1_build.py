#!/usr/bin/env python3
"""Compose HVM2 net for t5_rewrite_edges.

Minimal working version focusing on getting the basic structure right.
"""

import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, EDGE

P = Program()

# Primitives
lg = P.lg()
const_zero = P.const_trie("z0", 0)
hadd = P.update("hadd", "add")
to_list = P.to_list("tl")


def prog(d, c, edges):
    """Main program: rewrite edges under clustering."""

    # For now, create empty initial structures
    def step_c(builder, L, c_trie, idx, c_val):
        idx1, idx2 = builder.fanout(idx, 2)
        L1, L2 = builder.fanout(L, 2)
        c_trie_next = builder.call(hadd, t=c_trie, k=idx1, L=L1, P=c_val)
        idx_next = builder.op(idx2, "+", 1)
        return L2, c_trie_next, idx_next

    def fin_c(builder, L, c_trie, idx):
        builder.erase(idx)
        builder.erase(L)
        return c_trie

    w_c = P.stream("wc", step_c, fin_c,
                   state=[("L", DEPTH), ("c_trie", TRIE(NUM)), ("idx", NUM)],
                   elem=NUM)

    # Walk c to build c_trie
    # Initialize state: (L, zero_trie, 0)
    nm1 = 255  # max n-1
    L = d.call(lg, x=nm1)
    L1, L2 = d.fanout(L, 2)
    zero_trie = d.call(const_zero, L=L1)

    # Call the walker
    c_trie = d.call(w_c, list=c, init=(L2, zero_trie, 0))

    # Now process edges
    # For now, just skip edge processing and return empty list
    d.erase(c_trie)
    d.erase(edges)

    return d.nil()


def main():
    try:
        P.prog("t5_rewrite_edges", prog)
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm")
        P.write(output_path, "t5_rewrite_edges")
        print(f"Wrote {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
