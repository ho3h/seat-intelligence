#!/usr/bin/env python3
"""
t5_prop_conflicts: count property conflicts in clusters.

Algorithm: Group attributes by (node, key) and count occurrences.
Entries with count > 1 indicate conflicts.
Then map through clustering to get final (cluster_id, key) count.
"""

import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))

from genome.lib.glue import Program, NUM, DEPTH, TRIE, WEDGE

P = Program()

lg = P.lg()
zeros = P.const_trie("z0", 0)
inc = P.update("dinc", "inc")
reduce_gt1 = P.reduce("rgt1", lambda d, x: d.op(x, ">", 1), "+")

def step_fn(d, L, result_trie, node, key, value):
    """Count attrs per (node, key)."""
    L1, L2 = d.fanout(L, 2)
    # Create index: (node << 8) | key
    idx = d.op(node, "<<", 8)
    idx = d.op(idx, "|", key)
    result_trie_new = d.call(inc, t=result_trie, k=idx, L=L1)
    d.erase(value)
    return L2, result_trie_new

def fin_fn(d, L, result_trie):
    """Count entries with count > 1 (conflicts)."""
    L1, L2 = d.fanout(L, 2)
    d.erase(L2)
    return d.call(reduce_gt1, t=result_trie, L=L1)

stream_fn = P.stream("w", step_fn, fin_fn, state=[("L", DEPTH), ("t", TRIE(NUM))], elem=WEDGE)

def prog(d, c_list, attrs_list):
    """Main program - process attrs and count conflicts."""
    d.erase(c_list)

    # Depth for (node << 8) | key: need to handle node indices up to ~256 and key up to 3
    # So max index is around 256*256 = 65536, which needs depth 16
    L = 16
    L1, L2 = d.fanout(L, 2)

    result_trie = d.call(zeros, L=L1)
    return d.call(stream_fn, list=attrs_list, init=(L2, result_trie))

P.prog("t5_prop_conflicts", prog)
P.write(os.path.join(D, "net.hvm"))
print("Wrote net.hvm")
