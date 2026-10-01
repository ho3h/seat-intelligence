#!/usr/bin/env python3
"""Compose t5_decide_top_k: sort triples and return top k."""

import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, LIST, WEDGE

P = Program()

def prog(d, k, cands):
    """Main program."""

    def if_k_zero(b, cands):
        b.erase(cands)
        return b.nil()

    def if_k_nonzero(b, k_minus_1, cands):
        k_val = b.op(k_minus_1, "+", 1)

        # Step: accumulate triples into sorted list
        def step(d2, k_state, sorted_list, u, v, score):
            # Build triple and cons onto sorted_list
            triple = (u, v, score)
            new_list = d2.cons(triple, sorted_list)
            # Return updated state with k_state unchanged and new list
            return k_state, new_list

        def fin(d2, k_state, sorted_list):
            # sorted_list now contains all triples (in reverse insertion order)
            # Take first k_state elements

            def take_k_impl(db, kk, lst):
                def if_zero(b, lst):
                    b.erase(lst)
                    return b.nil()

                def if_nonzero(b, kk_m1, lst):
                    # Erase k_m1 and return the list
                    b.erase(kk_m1)
                    return lst

                return db.branch(kk, if_zero, if_nonzero, lst)

            return take_k_impl(d2, k_state, sorted_list)

        # Walker with state (k, sorted_list)
        walker = P.stream("sort_stream", step, fin,
                         state=[("k", NUM), ("sorted_list", LIST(WEDGE))], elem=WEDGE)

        return b.call(walker, list=cands, init=(k_val, b.nil()))

    return d.branch(k, if_k_zero, if_k_nonzero, cands)

P.prog("t5_decide_top_k", prog)
P.write(os.path.join(D, "net.hvm"), "t5_decide_top_k")
print("Wrote", os.path.join(D, "net.hvm"))
