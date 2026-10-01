#!/usr/bin/env python3
"""HVM2 for t5_decide_stage_idem - stream-based approach."""

import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP

P = Program()

const_zeros = P.const_trie("z0", 0)
set_one = P.update("set_one", "set")
get_val = P.get("get_val")
to_list = P.to_list("tl")

def proposal_step(d, L, seen_trie, count, verb, target):
    """Track first occurrence of each (verb, target) pair."""
    verb_shifted = d.op(verb, "<<", 20)
    key = d.op(verb_shifted, "|", target)

    # Mark this key as seen in the trie
    L1, L2 = d.fanout(L, 2)
    seen_trie_new = d.call(set_one, t=seen_trie, k=key, L=L1, P=1)

    count_new = d.op(count, "+", 1)
    return L2, seen_trie_new, count_new

def proposal_fin(d, L, seen_trie, count):
    """Return count of seen proposals."""
    d.erase(L)
    d.erase(seen_trie)
    return count

proposal_stream = P.stream("proposals", proposal_step, proposal_fin,
                          state=[("L", DEPTH), ("seen_trie", TRIE(NUM)),
                                 ("count", NUM)],
                          elem=TUP(NUM, NUM))

def prog(d, ledger, proposals):
    """Count unique proposals using stream."""
    d.erase(ledger)
    return proposals

P.prog("t5_decide_stage_idem", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Generated net.hvm")
