#!/usr/bin/env python3
"""Compose t5_decide_top_k: collect triples and return top k."""

import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, LIST, WEDGE

P = Program()

def prog(d, k, cands):
    """Main program."""

    def if_k_zero(b, cands):
        b.erase(cands)
        return b.nil()

    def if_k_nonzero(b, k_minus_1, cands):
        k_val = b.op(k_minus_1, "+", 1)

        # Step 1: collect all triples
        def collect_step(d2, k_st, collected, u, v, score):
            triple = (u, v, score)
            new_collected = d2.cons(triple, collected)
            return k_st, new_collected

        def collect_fin(d2, k_st, collected):
            # Now take first k elements from collected
            def take_step(d3, k_rem, result, u, v, score):
                # Check if k_rem > 0
                def if_zero_take(b, u_p, v_p, s_p, res_p):
                    # Stop taking
                    b.erase(u_p); b.erase(v_p); b.erase(s_p)
                    return 0, res_p

                def if_nonz_take(b, k_rm1, u_p, v_p, s_p, res_p):
                    # Take one element
                    tr = (u_p, v_p, s_p)
                    new_res = b.cons(tr, res_p)
                    return k_rm1, new_res

                return d3.branch(k_rem, if_zero_take, if_nonz_take, u, v, score, result)

            def take_fin(d3, k_rem, result):
                d3.erase(k_rem)
                return result

            take_walker = P.stream("take_walker", take_step, take_fin,
                                  state=[("k_rem", NUM), ("result", LIST(WEDGE))], elem=WEDGE)

            return d2.call(take_walker, list=collected, init=(k_st, d2.nil()))

        # Collect walker
        collect_walker = P.stream("collect_walker", collect_step, collect_fin,
                                 state=[("k_st", NUM), ("collected", LIST(WEDGE))], elem=WEDGE)

        return b.call(collect_walker, list=cands, init=(k_val, b.nil()))

    return d.branch(k, if_k_zero, if_k_nonzero, cands)

P.prog("t5_decide_top_k", prog)
P.write(os.path.join(D, "net.hvm"), "t5_decide_top_k")
print("Wrote", os.path.join(D, "net.hvm"))
