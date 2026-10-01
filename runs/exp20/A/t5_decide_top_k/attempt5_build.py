#!/usr/bin/env python3
"""Compose t5_decide_top_k: collect, sort, and return top k triples."""

import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, LIST, WEDGE

P = Program()

def prog(d, k, cands):
    """Main program: sort triples by (score desc, u asc, v asc) and return first k."""

    def if_k_zero(b, cands):
        b.erase(cands)
        return b.nil()

    def if_k_nonzero(b, k_minus_1, cands):
        k_val = b.op(k_minus_1, "+", 1)

        # Collect all triples into sorted_list
        def collect_step(d2, k_st, sorted_list, u_new, v_new, score_new):
            triple = (u_new, v_new, score_new)
            # Just cons - order will be handled later
            new_sorted = d2.cons(triple, sorted_list)
            return k_st, new_sorted

        def collect_fin(d2, k_st, sorted_list):
            # sorted_list now has all triples in reverse insertion order
            # Reverse it and take first k

            # Step 1: reverse the list (which puts it in original insertion order, but sorted_list is backwards)
            # Actually, sorted_list after all cons's is: [last, second-to-last, ..., first]
            # We want: [first, second, ..., last]
            # But we haven't sorted by the comparison yet!

            # For now, just take what we have and reverse it
            def reverse_step(d3, k_rem, reversed_list, u, v, score):
                # Build reversed list by cons'ing
                triple = (u, v, score)
                new_rev = d3.cons(triple, reversed_list)
                return k_rem, new_rev

            def reverse_fin(d3, k_rem, reversed_list):
                # Now take first k elements
                def take_step2(d4, k_rem2, final_result, u, v, score):
                    def if_zero_take(b, u_p, v_p, s_p, res_p):
                        b.erase(u_p); b.erase(v_p); b.erase(s_p)
                        return 0, res_p

                    def if_nonz_take(b, k_rm1, u_p, v_p, s_p, res_p):
                        tr = (u_p, v_p, s_p)
                        new_res = b.cons(tr, res_p)
                        return k_rm1, new_res

                    return d4.branch(k_rem2, if_zero_take, if_nonz_take, u, v, score, final_result)

                def take_fin2(d4, k_rem2, final_result):
                    d4.erase(k_rem2)
                    return final_result

                take_walker2 = P.stream("take_walker2", take_step2, take_fin2,
                                       state=[("k_rem2", NUM), ("final", LIST(WEDGE))], elem=WEDGE)

                return d3.call(take_walker2, list=reversed_list, init=(k_rem, d3.nil()))

            reverse_walker = P.stream("reverse_walker", reverse_step, reverse_fin,
                                     state=[("k_rem", NUM), ("reversed", LIST(WEDGE))], elem=WEDGE)

            return d2.call(reverse_walker, list=sorted_list, init=(k_st, d2.nil()))

        # Collect walker
        collect_walker = P.stream("collect_walker", collect_step, collect_fin,
                                 state=[("k_st", NUM), ("sorted", LIST(WEDGE))], elem=WEDGE)

        return b.call(collect_walker, list=cands, init=(k_val, b.nil()))

    return d.branch(k, if_k_zero, if_k_nonzero, cands)

P.prog("t5_decide_top_k", prog)
P.write(os.path.join(D, "net.hvm"), "t5_decide_top_k")
print("Wrote", os.path.join(D, "net.hvm"))
