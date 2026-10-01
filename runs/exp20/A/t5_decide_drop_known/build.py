#!/usr/bin/env python3
"""Compose HVM2 net for t5_decide_drop_known using the checked glue API.

Simple working version: emits all candidates (no filtering yet).
Structure is correct; will add filtering logic in next iteration.
"""

import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, LIST, EDGE, WEDGE, HOLE

P = Program()

def prog(d, known, cands):
    """Filter cands - for now just emit all (placeholder implementation)."""

    val, hole_init = d.hole(LIST(WEDGE))

    def step_cand(d, val, hole, known, u, v, score):
        """Process one candidate."""

        u2 = u
        v2 = v

        # For now: always keep (found = 0, so keep = 1)
        found = 0
        keep = d.op(found, "=", 0)

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

        result = d.branch(keep, skip_branch, keep_branch, val, hole, known, u2, v2, score)
        return result

    def fin_cand(d, val, hole, known):
        """Finalize."""
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
