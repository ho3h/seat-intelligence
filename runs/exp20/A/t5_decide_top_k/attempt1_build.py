#!/usr/bin/env python3
"""Compose t5_decide_top_k: sort triples by (score desc, u asc, v asc) and return top k."""

import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TUP, WEDGE, INF

P = Program()
# WEDGE = TUP(NUM, NUM, NUM) = (u, (v, (score, *)))

def prog(d, k, cands):
    """Main program: sort cands list of triples and return first k elements."""

    # Branch on k: if k == 0 return empty list, otherwise sort and take k
    def if_k_zero(b, cands):
        b.erase(cands)
        return b.nil()

    def if_k_nonzero(b, k_minus_1, cands):
        # k = k_minus_1 + 1
        k_val = b.op(k_minus_1, "+", 1)

        # For now, implement a simple pass-through that doesn't sort
        # but at least collects all the triples
        # We'll refine this to implement insertion sort later

        # The key insight: we need to return the input list itself
        # since sorting in HVM is complex

        # Actually, let's try to sort by collecting into a trie-based
        # approach using the library primitives

        # For a first pass, just return the cands list as-is
        # and take the first k elements

        def take_first_k(db, k_v, lst):
            """Recursively take first k elements."""
            def if_k_zero_inner(b, lst):
                b.erase(lst)
                return b.nil()

            def if_k_nonzero_inner(b, k_m1, lst):
                # k = k_m1 + 1
                # For now, erase k_m1 and just return the list
                b.erase(k_m1)
                return lst

            return db.branch(k_v, if_k_zero_inner, if_k_nonzero_inner, lst)

        return take_first_k(b, k_val, cands)

    return d.branch(k, if_k_zero, if_k_nonzero, cands)

P.prog("t5_decide_top_k", prog)
P.write(os.path.join(D, "net.hvm"), "t5_decide_top_k: placeholder")
print("Wrote", os.path.join(D, "net.hvm"))
