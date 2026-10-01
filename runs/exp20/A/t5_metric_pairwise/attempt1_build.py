#!/usr/bin/env python3
"""Build.py for t5_metric_pairwise"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, LIST, TUP

P = Program()

def prog(d, pred_list, truth_list):
    """Compute (tp, fp, fn) for pairwise confusion metrics."""
    # For now, just return (0, 0, 0)
    # We'll implement the algorithm iteratively
    d.erase(pred_list)
    d.erase(truth_list)
    return (0, 0, 0)

P.prog("t5_metric_pairwise", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Generated net.hvm")
