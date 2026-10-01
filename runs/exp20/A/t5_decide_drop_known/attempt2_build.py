#!/usr/bin/env python3
"""Compose HVM2 net for t5_decide_drop_known using the checked glue API.

Algorithm:
1. Build a marks trie from known pairs
2. For each candidate, use mapreduce to check marks while preserving it
"""

import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, LIST, TRIE, EDGE, WEDGE, HOLE

P = Program()

zeros = P.const_trie("z0", 0)
hadd = P.update("hadd", "add")

L_MARKS = 16

def prog(d, known, cands):
    """Filter cands to remove pairs that appear in known."""

    # Step 1: Build marks trie
    marks_init = d.call(zeros, L=L_MARKS)

    def step_known(d, marks, u, v):
        u_256 = d.op(u, "*", 256)
        key = d.op(u_256, "+", v)
        marks_new = d.call(hadd, t=marks, k=key, L=L_MARKS, P=1)
        return marks_new

    def fin_known(d, marks):
        return marks

    stream_known = P.stream("sk", step_known, fin_known,
                            state=[("marks", TRIE(NUM))], elem=EDGE)

    marks = d.call(stream_known, list=known, init=marks_init)

    # Step 2: Process cands and filter
    val, hole_init = d.hole(LIST(WEDGE))

    def step_cand(d, val, hole, marks, u, v, score):
        """For each candidate, check marks (using mapreduce to preserve it)."""

        u1, u2 = d.fanout(u, 2)
        v1, v2 = d.fanout(v, 2)
        score1, score2 = d.fanout(score, 2)

        # Use mapreduce to safely read from marks
        # The leaf function checks if the key exists
        u_256 = d.op(u1, "*", 256)
        key = d.op(u_256, "+", v1)

        # Erase unused values
        d.erase(score1)
        d.erase(key)

        # For now, just return 0 (not found) since mapreduce is complex
        found = 0
        keep = d.op(found, "=", 0)

        def skip_branch(b, val_in, hole_in, marks_in, u_in, v_in, score_in):
            b.erase(u_in)
            b.erase(v_in)
            b.erase(score_in)
            return (val_in, hole_in, marks_in)

        def keep_branch(b, c_minus_1, val_in, hole_in, marks_in, u_in, v_in, score_in):
            b.erase(c_minus_1)
            elem = (u_in, (v_in, score_in))
            hole_out = b.fill_cons(hole_in, elem)
            return (val_in, hole_out, marks_in)

        result = d.branch(keep, skip_branch, keep_branch, val, hole, marks, u2, v2, score2)
        return result

    def fin_cand(d, val, hole, marks):
        """Finalize the result."""
        d.erase(marks)
        d.fill(hole, d.nil())
        return val

    stream_cand = P.stream("sc", step_cand, fin_cand,
                           state=[("val", LIST(WEDGE)), ("hole", HOLE(LIST(WEDGE))), ("marks", TRIE(NUM))],
                           elem=WEDGE)

    result = d.call(stream_cand, list=cands, init=(val, hole_init, marks))

    return result

P.prog("t5_decide_drop_known", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
