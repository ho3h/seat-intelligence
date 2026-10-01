"""Build script for t5_decide_order (Condition B: recipes API).

Input: (tau, cands) where tau is a threshold 0..1000 and cands is a list of (u, v, score) triples.
Output: list of triples with score >= tau, sorted by descending score, then ascending u, then ascending v.
"""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, WEDGE
from genome.lib import recipes as R

P = Program()

# Filter to keep only triples with score >= tau
keep = R.filter_in_order(P, "keep", WEDGE, lambda d, u, v, s, tau: R.ge(d, s, tau), env=NUM)

# Sort by (1000 - score, u, v) to get descending score, then ascending u, then ascending v
# The key function returns a tuple of 3 elements
sort = R.sort_by(P, "sort", WEDGE, lambda d, u, v, s: (d.op(1000, "-", s), u, v))

def prog(d, tau, cands):
    # Filter the list to keep only those with score >= tau
    filtered = d.call(keep, list=cands, E=tau)
    # Sort the filtered list
    result = d.call(sort, list=filtered)
    return result

P.prog("t5_decide_order", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
