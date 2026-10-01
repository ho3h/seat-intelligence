"""
t5_decide_normalise: normalize pairs, deduplicate by max score, sort by (u, v).
Condition B: uses recipes (sort_by) + stream walker.
"""

import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, LIST, WEDGE, INF
from genome.lib import recipes as R

P = Program()

# Key function: extract (min(u,v), max(u,v), 16777215-score)
def key_fn(d, u, v, s):
    min_val, max_val = R.min2(d, u, v)
    return (min_val, max_val, d.op(16777215, "-", s))

# Recipe instance: sort by (min(u,v), max(u,v), 16777215-score)
sort_rec = R.sort_by(P, "sort_wedges", WEDGE, key_fn)

# Define step and fin at top level for the stream walker
def step(d, result_list, u, v, s):
    # Compute (min, max) for this element
    min_uv, max_uv = R.min2(d, u, v)

    # Create normalized triple and prepend
    triple = (min_uv, max_uv, s)
    new_list = d.cons(triple, result_list)

    return new_list

def fin(d, result_list):
    return result_list

# Create walker primitive
walker = P.stream("dedup_walker", step, fin,
                  state=[("result_list", LIST(WEDGE))],
                  elem=WEDGE)

def prog(d, cands):
    # Step 1: sort by (min(u,v), max(u,v), -score)
    sorted_list = d.call(sort_rec, list=cands)

    # For now, just return sorted_list to test if sorting works
    return sorted_list

P.prog("t5_decide_normalise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
