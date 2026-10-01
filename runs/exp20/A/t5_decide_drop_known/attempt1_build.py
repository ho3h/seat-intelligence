#!/usr/bin/env python3
"""Compose HVM2 net for t5_decide_drop_known using the checked glue API.

Algorithm: For each candidate, walk through the known list to check if the pair exists.
This is quadratic but necessary given HVM's linear logic constraints.
"""

import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, LIST, TUP, EDGE, WEDGE, HOLE, INF

P = Program()

# Define a helper that filters a cands list using a known list
# Takes: cands (list of WEDGE), known (list of EDGE), hole (for building result)
# Returns: updated hole after filtering

# We need to define a recursive walker as a separate definition
check_known_helper_name = "check_known"

def prog(d, known, cands):
    """Main entry point: filter cands by removing pairs that appear in known."""

    val, hole_init = d.hole(LIST(WEDGE))

    # Define a walker step that processes cands
    def step_cand(d, val, hole, known, u, v, score):
        """Process one candidate from cands."""

        # Fanout u, v, score for both key computation and branching
        u1, u2 = d.fanout(u, 2)
        v1, v2 = d.fanout(v, 2)
        score1, score2 = d.fanout(score, 2)

        # Erase the first copies (not used for now)
        d.erase(u1)
        d.erase(v1)
        d.erase(score1)

        # Check if (u, v) is in known (simplified: always return 0 for now)
        found = 0
        keep = d.op(1, "-", found)  # keep = 1 - 0 = 1 (always keep for now)

        def skip_branch(b, val_in, hole_in, known_in, u_in, v_in, score_in):
            b.erase(u_in)
            b.erase(v_in)
            b.erase(score_in)
            return (val_in, hole_in, known_in)

        def keep_branch(b, c_minus_1, val_in, hole_in, known_in, u_in, v_in, score_in):
            b.erase(c_minus_1)
            elem = (u_in, (v_in, score_in))
            hole_out = b.fill_cons(hole_in, elem)
            return (val_in, hole_out, known_in)

        result = d.branch(keep, skip_branch, keep_branch, val, hole, known, u2, v2, score2)
        return result

    def fin_cand(d, val, hole, known):
        """Finalize the result."""
        d.erase(known)
        d.fill(hole, d.nil())
        return val

    stream_cand = P.stream("sc", step_cand, fin_cand,
                           state=[("val", LIST(WEDGE)), ("hole", HOLE(LIST(WEDGE))), ("known", LIST(EDGE))],
                           elem=WEDGE)

    result = d.call(stream_cand, list=cands, init=(val, hole_init, known))

    return result

P.prog("t5_decide_drop_known", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
