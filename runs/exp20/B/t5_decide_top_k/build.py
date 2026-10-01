#!/usr/bin/env python3
"""
Composition of t5_decide_top_k using genome.lib.glue (checked API) and genome.lib.recipes.

Contract: Given k >= 0 and a list of candidate triples (u, v, score), return the first k triples
sorted by descending score, ties broken by ascending u, then ascending v.
"""

import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")

from genome.lib.glue import Program, NUM, LIST, WEDGE, ANY
from genome.lib import recipes as R


def build():
    P = Program()

    # Recipe instances:
    # 1. sort_by: sorts the list by a key function (ascending)
    # 2. take_first: takes the first k elements

    sort_recipe = R.sort_by(P, "sort", WEDGE,
                            lambda d, u, v, s: (d.op(1000, "-", s), u, v))
    take_recipe = R.take_first(P, "take", WEDGE)

    def prog(d, k, cands):
        # Sort candidates by (descending score, ascending u, ascending v)
        sorted_cands = d.call(sort_recipe, list=cands)

        # Take the first k elements
        result, rest = d.call(take_recipe, list=sorted_cands, k=k)
        d.erase(rest)

        return result

    P.prog("t5_decide_top_k", prog)
    return P


if __name__ == "__main__":
    P = build()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm")
    P.write(path)
    print(f"Wrote {path}")
