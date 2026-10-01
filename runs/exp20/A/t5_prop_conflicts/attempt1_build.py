#!/usr/bin/env python3
"""
t5_prop_conflicts: count property conflicts in clusters.
"""

import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))

from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, WEDGE, INF

P = Program()

# Primitives
lg = P.lg()
zeros = P.const_trie("z0", 0)
get_prim = P.get("gt")
inc_prim = P.update("dinc", "inc")

def step_fn(d, L, attrs_trie, node, key, value):
    """Process one attribute."""
    L1, L2 = d.fanout(L, 2)

    # Compute key: (node << 8) | key
    comp_key = d.op(node, "<<", 8)
    comp_key = d.op(comp_key, "|", key)

    # Increment attrs_trie at this key
    attrs_trie_new = d.call(inc_prim, t=attrs_trie, k=comp_key, L=L1)

    d.erase(value)
    return L2, attrs_trie_new

def fin_fn(d, L, attrs_trie):
    """Finalize."""
    d.erase(L, attrs_trie)
    return 0

stream_attrs = P.stream("attrs", step_fn, fin_fn,
    state=[("L", DEPTH), ("a", TRIE(NUM))],
    elem=WEDGE
)

def prog(d, c_list, attrs_list):
    """Main program."""
    d.erase(c_list, attrs_list)
    return 0

P.prog("t5_prop_conflicts", prog)

output_path = os.path.join(D, "net.hvm")
P.write(output_path)
print(f"Wrote {output_path}")
