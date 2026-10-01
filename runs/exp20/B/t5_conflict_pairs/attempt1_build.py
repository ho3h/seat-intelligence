#!/usr/bin/env python3
"""Build script for t5_conflict_pairs: output violated must-not-link pairs sorted lexicographically.

Input: (c, mnl) where c is a clustering (list of canonical ids) and mnl is a list of (a, b) pairs
Output: list of violated pairs (where c[a] == c[b]) sorted ascending lexicographically
"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, EDGE, TRIE, INF, HOLE, MCQ
from genome.lib import recipes as R

P = Program()

# Primitives needed
lc = R.list_length_and_copy(P, "lc", NUM, copies=1)
tri = R.list_to_trie(P, "tri", NUM)
sort_pairs = R.sort_by(P, "sort", EDGE, lambda d, a, b: (a, b))
mc_empty = P.mc_empty("zq")
mc_request = P.mc_request("rq")
mc_deliver = P.mc_deliver("dv")

# Stream walker: for each pair (a, b), queue lookups and check if c[a] == c[b]
def step(d, L, q, h, a_elem, b_elem):
    # Fanout L for the two mc_request calls and for returning in state
    L1, L2, L3 = d.fanout(L, 3)

    # Fanout a and b since they're needed for the requests and the branch
    a1, a2 = d.fanout(a_elem, 2)
    b1, b2 = d.fanout(b_elem, 2)

    # Queue lookup requests for a and b
    c_a, q1 = d.call(mc_request, q=q, k=a1, L=L1)
    c_b, q2 = d.call(mc_request, q=q1, k=b1, L=L2)

    # Check if c[a] == c[b]
    equal = d.op(c_a, "=", c_b)

    def skip(b, h_arg, a_arg, b_arg):
        b.erase(a_arg, b_arg)
        return h_arg

    def keep(b, eq_m1, h_arg, a_arg, b_arg):
        b.erase(eq_m1)
        return b.fill_cons(h_arg, (a_arg, b_arg))

    h2 = d.branch(equal, skip, keep, h, a2, b2)
    return L3, q2, h2

def fin(d, L, q, h):
    d.erase(L)
    d.fill(h, d.nil())
    return q  # Return the final request trie so mc_deliver can use it

w = P.stream("w", step, fin, state=[("L", DEPTH), ("q", MCQ), ("h", HOLE(LIST(EDGE)))], elem=EDGE)

def prog(d, c, mnl):
    # Get length of c and build a copy
    n, c_copy = d.call(lc, list=c)

    # Handle empty clustering case
    def handle_empty_c(b, c_copy, mnl):
        b.erase(c_copy, mnl)
        return b.nil()

    def handle_nonempty_c(b, nm1, c_copy, mnl):
        # Build trie from c_copy for lookups
        n_plus_1 = b.op(nm1, "+", 1)
        L = R.depth_for(P, b, n_plus_1)
        L1, L2, L3, L4 = b.fanout(L, 4)  # Four copies: one for trie, one for mc_empty, one for walker, one for mc_deliver
        c_trie = b.call(tri, list=c_copy, L=L1)

        # Create empty request trie
        q_empty = b.call(mc_empty, L=L2)

        # Create hole for the violations list
        violations_val, violations_hole = b.hole(LIST(EDGE))

        # Walk mnl and queue requests, fill violations
        q_final = b.call(w, list=mnl, init=(L3, q_empty, violations_hole))

        # Deliver values from c_trie into the request trie
        b.call(mc_deliver, v=c_trie, q=q_final, L=L4)

        # Sort and return violations
        return b.call(sort_pairs, list=violations_val)

    return d.branch(n, handle_empty_c, handle_nonempty_c, c_copy, mnl)

P.prog("t5_conflict_pairs", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
