"""
t5_decide_drop_known: Minimal version - just return cands
"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program

P = Program()

def prog(d, known, cands):
    # Minimal: just return cands without filtering
    d.erase(known)
    return cands

P.prog("t5_decide_drop_known", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net_minimal.hvm"))
print("Built net_minimal.hvm")
