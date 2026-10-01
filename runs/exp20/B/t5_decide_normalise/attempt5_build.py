"""
t5_decide_normalise: normalize pairs, deduplicate by max score, sort by (u, v).
Condition B: uses recipes (sort_by + list_to_trie + select_sorted).
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

# Recipe instances
sort_rec = R.sort_by(P, "sort_wedges", WEDGE, key_fn)
len_copy = R.list_length_and_copy(P, "lc", WEDGE)
to_trie = R.list_to_trie(P, "lt", WEDGE)
def pred_fn(d, x, i, E):
    # x is a WEDGE tuple, keep all
    d.erase(x)
    d.erase(i)
    d.erase(E)
    return 1

def emit_fn(d, x, i, E):
    # x is a WEDGE tuple (u, v, s), emit normalized
    u, v, s = d.split(x)
    d.erase(i)
    d.erase(E)
    min_uv, max_uv = R.min2(d, u, v)
    return (min_uv, max_uv, s)

select = R.select_sorted(P, "sel", pred_fn, emit_fn, leaf_kind=WEDGE, env=NUM)

def prog(d, cands):
    # Step 1: sort by (min(u,v), max(u,v), -score)
    sorted_list = d.call(sort_rec, list=cands)

    # Step 2: get length and depth
    n, sorted_copy = d.call(len_copy, list=sorted_list)
    n_depth, n_sel = d.fanout(n, 2)
    L = R.depth_for(P, d, n_depth)
    L_trie, L_sel_depth = d.fanout(L, 2)

    # Step 3: convert to trie
    sorted_trie = d.call(to_trie, list=sorted_copy, L=L_trie)

    # Step 4: select and emit normalized pairs
    result = d.call(select, t=sorted_trie, L=L_sel_depth, E=n_sel)

    return result

P.prog("t5_decide_normalise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
