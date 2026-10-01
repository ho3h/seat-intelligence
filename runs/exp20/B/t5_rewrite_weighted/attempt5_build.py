#!/usr/bin/env python3
"""
t5_rewrite_weighted: Weighted edge rewrite with clustering.

Input: (c, edges) where c is a clustering (list of canonical ids) and
       edges is a list of (u, v, w) triples.
Output: Sorted list of (x, y, total) where total is the sum of weights
        for each distinct rewritten edge pair (x, y), with x < y and x != y.
"""

import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")

from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, WEDGE, TUP, INF
from genome.lib import recipes as R

P = Program()

# Recipe instances for composition

# 1. Get length of clustering and make a copy
lc = R.list_length_and_copy(P, "lc", NUM)

# 2. Convert clustering to trie for lookups
ct = R.list_to_trie(P, "ct", NUM)

# 3. Look up c[u] and c[v] for each edge
lk = R.lookup_many(P, "lk", WEDGE, lambda d, u, v, w: (u, v), nkeys=2)

# 4. Filter to keep only cross-cluster edges (c[u] != c[v])
def filter_cross_cluster(d, u, v, w, c_u, c_v):
    # Keep if c_u != c_v
    eq = d.op(c_u, "=", c_v)
    # eq is 1 if equal, 0 if not equal (in HVM, "=" checks equality)
    # We want to keep if NOT equal, so return 1 - eq
    return d.op(1, "-", eq)

filt = R.filter_in_order(P, "filt", TUP(NUM, NUM, NUM, NUM, NUM), filter_cross_cluster)

# 5. Reduce by key: group by (min(c[u], c[v]), max(c[u], c[v])) and sum weights
def keyval_fn(d, u, v, w, c_u, c_v):
    # Compute min and max
    min_c, max_c = R.min2(d, c_u, c_v)
    # Pack: key = (min_c << 12) | max_c
    key = d.op(d.op(min_c, "<<", 12), "|", max_c)
    return (key, w)

# elem type is TUP(NUM, NUM, NUM, NUM, NUM) for (u, v, w, c_u, c_v)
rk = R.reduce_by_key(P, "rk", TUP(NUM, NUM, NUM, NUM, NUM), keyval_fn, "add", ident=0)

# 6. Select sorted: emit in sorted order
def pred_fn(d, x, i, E):
    # Keep only if x > 0 (there were actual edges)
    return R.not0(d, x)

def emit_fn(d, x, i, E):
    # Unpack the key
    # i is the packed key = (min_c << 12) | max_c
    # Compute min_c and max_c from i
    i1, i2 = d.fanout(i, 2)
    min_c = d.op(i1, ">>", 12)
    max_c = d.op(i2, "&", 4095)
    return (min_c, max_c, x)

sel = R.select_sorted(P, "sel", pred_fn, emit_fn, leaf_kind=NUM, env=NUM)

def prog(d, c, edges):
    # Get length of clustering and a copy
    n, c_copy = d.call(lc, list=c)

    # Branch on n == 0
    def empty(b, c_copy, edges):
        b.erase(c_copy)
        b.erase(edges)
        return b.nil()

    def nonempty(b, nm1, c_copy, edges):
        # nm1 = n - 1
        # Compute n
        n = b.op(nm1, "+", 1)
        # Fanout n for multiple uses
        n1, n2 = b.fanout(n, 2)

        # Get depth for clustering
        depth = R.depth_for(P, b, n1)

        # Fanout depth for multiple uses
        d1, d2, d3 = b.fanout(depth, 3)

        # Build trie from clustering
        c_trie = b.call(ct, list=c_copy, L=d1)

        # Look up c[u] and c[v] for each edge
        edges_with_c = b.call(lk, list=edges, V=c_trie, L=d2)

        # Filter to keep only cross-cluster edges
        filtered = b.call(filt, list=edges_with_c)

        # Reduce by key to group and sum
        grouped = b.call(rk, list=filtered, L=d3)

        # Select sorted to emit in order
        pair_depth = R.depth_for(P, b, b.op(n2, "*", 2))
        return b.call(sel, t=grouped, L=pair_depth, E=0)

    return d.branch(n, empty, nonempty, c_copy, edges)

P.prog("t5_rewrite_weighted", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("wrote net.hvm")
