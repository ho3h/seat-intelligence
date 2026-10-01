#!/usr/bin/env python3
"""Build the HVM2 net for t5_decide_filter."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
# /Users/tedsandtads/Genome/runs/exp14/unchecked/t5_decide_filter
# -> /Users/tedsandtads/Genome
genome_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D))))
sys.path.insert(0, genome_root)
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

K = 16  # walker lookahead


def t5_decide_filter():
    """Input: (tau, cands) where tau is a threshold and cands is a list of (u (v score)) triples.
    Output: list of triples where score >= tau, in original order, keeping duplicates.

    Algorithm: stream walker with state (tau acc) where acc is the accumulating output list.
    For each triple, check if score >= tau and either prepend to acc or skip.
    """
    b = Book()

    # stream walker: processes cands, maintains state (tau acc)
    # step: check if score >= tau, if yes prepend to accumulator
    # fin: extract acc from final state (tau acc)
    G.stream(b, "w", K,
        """((t1 acc) ((u (v score)) (t2a acc2)))
  & t1 ~ t2
  & t2 ~ {t2a t2b}
  & score ~ {s1 s2}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & s2 ~ $([<] $(t2b lt))
  & lt ~ ?((@w_skip @w_take) ((acc2 (u1 (v1 s1))) acc))
  & u2 ~ *
  & v2 ~ *""",
        "((* a) a)")

    # Helper branches for the filter decision
    # Context: ((acc2 (u (v score))) acc)
    # @w_skip: score < tau (skip this triple, keep acc unchanged)
    # Matches: ((x c) a) -> outputs x (acc2 stays as is)
    # Erase unused c and a since we're keeping acc unchanged
    # @w_take: score >= tau (prepend this triple)
    # Matches: (* ((x c) a)) -> outputs (1 (c a)) (prepend triple to acc)
    # Erase unused x
    b.add("""
@w_skip = (((x *) *) x)
@w_take = (* (((* c) a) (1 (c a))))
@prog = ((tau cands) out)
  & @w_blk ~ (cands ((tau (0 *)) out))
""")

    return b


if __name__ == "__main__":
    path = os.path.join(D, "net.hvm")
    open(path, "w").write(t5_decide_filter().text())
    print("wrote", path)
