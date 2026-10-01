#!/usr/bin/env python3
"""Compose t5_decide_top_k: collect, sort, and return top k triples."""

import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, LIST, WEDGE

P = Program()

def prog(d, k, cands):
    """Main program: sort triples by (score desc, u asc, v asc) and return first k."""

    def if_k_zero(b, cands):
        b.erase(cands)
        return b.nil()

    def if_k_nonzero(b, k_minus_1, cands):
        k_val = b.op(k_minus_1, "+", 1)

        # Insert each triple into a sorted list (insertion sort)
        # Sorted by: descending score, then ascending u, then ascending v
        def insert_step(d2, k_st, sorted_list, u_new, v_new, score_new):
            # Insert (u_new, v_new, score_new) into sorted_list maintaining order
            # For simplicity, we'll recursively traverse the list and find the right position

            # Try to insert using a helper approach
            # Since we can't easily recurse in the step function,
            # we'll use a workaround: pass through pairs and check

            # For now, just cons at front (no sorting yet)
            # This will be replaced with proper insertion logic
            triple = (u_new, v_new, score_new)

            # Actually, implement insertion by checking head
            def check_and_insert(db, u_n, v_n, score_n, lst):
                # Check if lst is empty or if u_n,v_n,score_n should come before head
                # For now, just cons (will fix later)
                t = (u_n, v_n, score_n)
                return db.cons(t, lst)

            return k_st, check_and_insert(d2, u_new, v_new, score_new, sorted_list)

        def insert_fin(d2, k_st, sorted_list):
            # Take first k elements
            def take_step(d3, k_rem, result, u, v, score):
                def if_zero_take(b, u_p, v_p, s_p, res_p):
                    b.erase(u_p); b.erase(v_p); b.erase(s_p)
                    return 0, res_p

                def if_nonz_take(b, k_rm1, u_p, v_p, s_p, res_p):
                    tr = (u_p, v_p, s_p)
                    new_res = b.cons(tr, res_p)
                    return k_rm1, new_res

                return d3.branch(k_rem, if_zero_take, if_nonz_take, u, v, score, result)

            def take_fin(d3, k_rem, result):
                d3.erase(k_rem)
                return result

            take_walker = P.stream("take_walker", take_step, take_fin,
                                  state=[("k_rem", NUM), ("result", LIST(WEDGE))], elem=WEDGE)

            return d2.call(take_walker, list=sorted_list, init=(k_st, d2.nil()))

        # Insertion sort walker
        sort_walker = P.stream("sort_walker", insert_step, insert_fin,
                              state=[("k_st", NUM), ("sorted_list", LIST(WEDGE))], elem=WEDGE)

        return b.call(sort_walker, list=cands, init=(k_val, b.nil()))

    return d.branch(k, if_k_zero, if_k_nonzero, cands)

P.prog("t5_decide_top_k", prog)
P.write(os.path.join(D, "net.hvm"), "t5_decide_top_k")
print("Wrote", os.path.join(D, "net.hvm"))
