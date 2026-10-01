"""
t5_decide_drop_known: Minimal - just return cands (no filtering yet).
"""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program

P = Program()

def prog(d, known, cands):
    d.erase(known)
    return cands

P.prog("t5_decide_drop_known", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
