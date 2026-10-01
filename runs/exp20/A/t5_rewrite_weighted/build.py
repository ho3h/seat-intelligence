"""Build t5_rewrite_weighted: return empty list (baseline)."""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program

P = Program()

# Main program - just return empty list for now
def prog(d, c_list, es_list):
    d.erase(c_list)
    d.erase(es_list)
    return d.nil()

P.prog("t5_rewrite_weighted", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Wrote net.hvm")
