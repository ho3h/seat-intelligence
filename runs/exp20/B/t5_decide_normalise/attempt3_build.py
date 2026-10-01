"""
t5_decide_normalise: normalize pairs, deduplicate by max score, sort by (u, v).
Condition B: uses recipes (sort_by) + stream walker.
"""

import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, LIST, WEDGE, INF
from genome.lib import recipes as R

P = Program()

# Key function: extract (min(u,v), max(u,v), 16777215-score)
def key_fn(d, u, v, s):
    min_val, max_val = R.min2(d, u, v)
    return (min_val, max_val, d.op(16777215, "-", s))

# Recipe instance: sort by (min(u,v), max(u,v), 16777215-score)
sort_rec = R.sort_by(P, "sort_wedges", WEDGE, key_fn)

def prog(d, cands):
    # Step 1: sort by (min(u,v), max(u,v), -score)
    sorted_list = d.call(sort_rec, list=cands)

    # Step 2: walk through sorted list, deduplicating by (min, max) pair
    def step(d, prev_min, prev_max, result_list, u, v, s):
        # Compute (min, max) for this element
        min_uv, max_uv = R.min2(d, u, v)

        # Fanout for comparison and using in triple + return
        min_cmp, min_rest = d.fanout(min_uv, 2)
        max_cmp, max_rest = d.fanout(max_uv, 2)

        # Fanout again for triple and return
        min_triple, min_return = d.fanout(min_rest, 2)
        max_triple, max_return = d.fanout(max_rest, 2)

        # Fanout prev_min/prev_max
        prev_min_cmp, prev_min_use = d.fanout(prev_min, 2)
        prev_max_cmp, prev_max_use = d.fanout(prev_max, 2)

        # Check if this is a new pair
        min_eq = d.op(min_cmp, "=", prev_min_cmp)
        max_eq = d.op(max_cmp, "=", prev_max_cmp)
        same_pair = d.op(min_eq, "&", max_eq)
        is_new = d.op(same_pair, "!", 0)

        # Branches
        def append_elem(b, cm1, prev_min, prev_max, result_list, min_triple, max_triple, s, min_return, max_return):
            b.erase(cm1)
            b.erase(prev_min)
            b.erase(prev_max)
            # Create normalized triple as a flat tuple
            triple = (min_triple, max_triple, s)
            new_list = b.cons(triple, result_list)
            return min_return, max_return, new_list

        def skip_elem(b, prev_min, prev_max, result_list, min_triple, max_triple, s, min_return, max_return):
            b.erase(s)
            b.erase(min_triple)
            b.erase(max_triple)
            b.erase(min_return)
            b.erase(max_return)
            return prev_min, prev_max, result_list

        return d.branch(is_new, skip_elem, append_elem,
                       prev_min_use, prev_max_use, result_list, min_triple, max_triple, s, min_return, max_return)

    def fin(d, prev_min, prev_max, result_list):
        d.erase(prev_min)
        d.erase(prev_max)
        return result_list

    walker = P.stream("dedup_walker", step, fin,
                      state=[("prev_min", NUM), ("prev_max", NUM), ("result_list", LIST(WEDGE))],
                      elem=WEDGE)

    # Run walker and return result (output is in reverse order)
    return d.call(walker, list=sorted_list, init=(INF, INF, d.nil()))

P.prog("t5_decide_normalise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
