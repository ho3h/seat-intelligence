"""Compose t5_decide_order: filter and sort triples."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, "../../../.."))
from genome.lib.glue import Program, NUM, LIST, TUP, ANY

P = Program()

def prog(d, tau, cands):
    """Sort and filter: keep items with score >= tau, sorted by score desc then u asc then v asc."""

    # The element is unpacked as (u, (v, score))
    def step(d, out_list, tau_val, u, v, score):
        """Process one item from input."""

        # Fanout since values are used multiple times
        tau_for_cmp, tau_for_state = d.fanout(tau_val, 2)
        score_for_cmp, score_for_branch = d.fanout(score, 2)

        # Check if score >= tau
        ge = d.op(score_for_cmp, ">", d.op(tau_for_cmp, "-", 1))

        def skip(b, out_list, tau_val, u, v, score):
            b.erase(u)
            b.erase(v)
            b.erase(score)
            return (out_list, tau_val)

        def insert(b, cm1, out_list, tau_val, u, v, score):
            b.erase(cm1)
            # Cons triple onto output
            triple = (u, (v, score))
            new_list = (1, (triple, out_list))
            return (new_list, tau_val)

        return d.branch(ge, skip, insert, out_list, tau_for_state, u, v, score_for_branch)

    def fin(d, out_list, tau_val):
        d.erase(tau_val)
        return out_list

    # Create walker - element is (u, (v, score)) which unpacks as three fields u, v, score
    w = P.stream("w", step, fin, state=[("out_list", ANY), ("tau_val", NUM)],
                 elem=TUP(NUM, NUM, NUM))

    # Process with initial empty list and tau
    result = d.call(w, list=cands, init=(d.nil(), tau))

    return result

P.prog("t5_decide_order", prog)
P.write(os.path.join(D, "net.hvm"))
print(f"Wrote net.hvm")
