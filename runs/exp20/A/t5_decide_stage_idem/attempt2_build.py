#!/usr/bin/env python3
"""HVM2 for t5_decide_stage_idem."""

import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP

P = Program()

const_zeros = P.const_trie("z0", 0)
to_list = P.to_list("tl")

def prog(d, ledger, proposals):
    """Placeholder - return proposals unchanged."""
    d.erase(ledger)
    return proposals

P.prog("t5_decide_stage_idem", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Generated net.hvm")
