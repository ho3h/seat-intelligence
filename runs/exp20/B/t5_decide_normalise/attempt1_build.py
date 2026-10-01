"""
t5_decide_normalise: normalize pairs, deduplicate by max score, sort by (u, v).
Condition B: uses recipes (sort_by) + stream walker with hole.
"""

import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, LIST, WEDGE, HOLE, INF
from genome.lib import recipes as R

P = Program()

# Key function: extract (min(u,v), max(u,v), 16777215-score)
def key_fn(d, u, v, s):
    min_val, max_val = R.min2(d, u, v)
    return (min_val, max_val, d.op(16777215, "-", s))

# Recipe instance: sort by (min(u,v), max(u,v), 16777215-score)
# This puts max scores first for each normalized pair
sort_rec = R.sort_by(P, "sort_wedges", WEDGE, key_fn)

def prog(d, cands):
    # Step 1: sort by (min(u,v), max(u,v), -score)
    sorted_list = d.call(sort_rec, list=cands)

    # Step 2: create output list with hole
    result_val, result_hole = d.hole(LIST(WEDGE))

    # Step 3: walk through sorted list, deduplicating by (min, max) pair
    def step(d, prev_min, prev_max, hole, u, v, s):
        # Compute (min, max) for this element
        u1, u2 = d.fanout(u, 2)
        v1, v2 = d.fanout(v, 2)
        min_uv, max_uv = R.min2(d, u1, v1)

        # Fanout min/max for both comparison and state return
        min_cmp, min_ret = d.fanout(min_uv, 2)
        max_cmp, max_ret = d.fanout(max_uv, 2)

        # Fanout prev_min/prev_max for both comparison and passing to branches
        prev_min_cmp, prev_min_pass = d.fanout(prev_min, 2)
        prev_max_cmp, prev_max_pass = d.fanout(prev_max, 2)

        # Check if this is a new pair (different from previous)
        min_eq = d.op(min_cmp, "=", prev_min_cmp)
        max_eq = d.op(max_cmp, "=", prev_max_cmp)
        same_pair = d.op(min_eq, "&", max_eq)
        is_new = d.op(same_pair, "!", 0)

        # Zero branch: is_new == 0, skip element (duplicate)
        def skip_elem(b, prev_min, prev_max, hole, u2, v2, s, min_ret, max_ret):
            b.erase(u2)
            b.erase(v2)
            b.erase(s)
            b.erase(min_ret)
            b.erase(max_ret)
            return prev_min, prev_max, hole

        # Nonzero branch: is_new > 0, append element (new pair)
        def append_elem(b, cm1, prev_min, prev_max, hole, u2, v2, s, min_ret, max_ret):
            b.erase(cm1)
            b.erase(prev_min)
            b.erase(prev_max)
            new_hole = b.fill_cons(hole, (u2, (v2, s)))
            return min_ret, max_ret, new_hole

        return d.branch(is_new, skip_elem, append_elem,
                       prev_min_pass, prev_max_pass, hole, u2, v2, s, min_ret, max_ret)

    def fin(d, prev_min, prev_max, hole):
        d.erase(prev_min)
        d.erase(prev_max)
        d.fill(hole, d.nil())
        return d.nil()

    walker = P.stream("dedup_walker", step, fin,
                      state=[("prev_min", NUM), ("prev_max", NUM), ("hole", HOLE(LIST(WEDGE)))],
                      elem=WEDGE)

    # Initialize walker with sentinel values that won't match any real pair
    _ = d.call(walker, list=sorted_list, init=(INF, INF, result_hole))
    d.erase(_)

    return result_val

P.prog("t5_decide_normalise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
