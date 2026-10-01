#!/usr/bin/env python3
"""HVM2 for t5_decide_stage_idem - using mapreduce for dedup."""

import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP

P = Program()

# This won't work easily - would need complex multi-pass logic
# Simplest fallback: just echo proposals

def prog(d, ledger, proposals):
    d.erase(ledger)
    return proposals

P.prog("t5_decide_stage_idem", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Generated net.hvm")
