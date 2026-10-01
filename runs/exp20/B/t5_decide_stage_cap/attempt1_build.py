import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, EDGE, WEDGE, HOLE, INF
from genome.lib import recipes as R

P = Program()

# Filter by score >= tau (keep only accepted triples)
filter_keep = R.filter_in_order(P, "filter_keep", WEDGE,
    lambda d, u, v, s, tau: R.ge(d, s, tau), env=NUM)

# Sort by (1000 - score, u, v) for descending score with ascending u, v on ties
sort_it = R.sort_by(P, "sort_it", WEDGE,
    lambda d, u, v, s: (d.op(1000, "-", s), u, v))

# Take first cap elements from sorted list
take_it = R.take_first(P, "take_it", WEDGE)

# Stream to drop scores from WEDGE (u, v, score) -> EDGE (u, v)
# Uses hole mechanism to build list in correct order
def drop_step(d, val, hole, u, v, s):
    d.erase(s)  # Don't need the score
    new_hole = d.fill_cons(hole, d.split((u, v)))
    return (val, new_hole)

def drop_fin(d, val, hole):
    d.fill(hole, d.nil())
    return val

drop_scores = P.stream("drop_scores", drop_step, drop_fin,
    state=[("val", LIST(EDGE)), ("hole", HOLE(LIST(EDGE)))], elem=WEDGE)

# Main program
def prog(d, tau, cap, cands):
    # Step 1: Filter to keep only accepted triples (score >= tau)
    filtered = d.call(filter_keep, list=cands, E=tau)

    # Step 2: Sort by descending score, then by ascending u and v
    sorted_list = d.call(sort_it, list=filtered)

    # Step 3: Take first cap elements, get deferred count
    staged_with_scores, deferred = d.call(take_it, list=sorted_list, k=cap)

    # Step 4: Drop scores to convert WEDGE -> EDGE using hole mechanism
    val, hole = d.hole(LIST(EDGE))
    staged = d.call(drop_scores, list=staged_with_scores, init=(val, hole))

    return (staged, deferred)

P.prog("t5_decide_stage_cap", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
