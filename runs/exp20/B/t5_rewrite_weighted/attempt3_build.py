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
# Input: list of (u, v, w), Output: list of (u, v, w, c[u], c[v])
lk = R.lookup_many(P, "lk", WEDGE, lambda d, u, v, w: (u, v), nkeys=2)

# 4. Reduce by key: group by (min(c[u], c[v]), max(c[u], c[v])) and sum weights
# Skip edges where c[u] == c[v] by returning 0 weight
def keyval_fn(d, u, v, w, c_u, c_v):
    # Compute min and max
    min_c, max_c = R.min2(d, c_u, c_v)
    # Fanout min_c and max_c for two uses each
    min_c1, min_c2 = d.fanout(min_c, 2)
    max_c1, max_c2 = d.fanout(max_c, 2)
    # Pack them: key = (min_c << 12) | max_c
    # This handles vertex ids up to 4095 (sufficient for n <= 144)
    key = d.op(d.op(min_c1, "<<", 12), "|", max_c1)
    # Skip edges where c[u] == c[v] by returning w=0
    eq = d.op(min_c2, "=", max_c2)
    w_adj = d.select(eq, 0, w)  # If equal, return 0; else return w
    return (key, w_adj)

# elem type is TUP(NUM, NUM, NUM, NUM, NUM) for (u, v, w, c_u, c_v)
rk = R.reduce_by_key(P, "rk", TUP(NUM, NUM, NUM, NUM, NUM), keyval_fn, "add", ident=0)

# 5. Select sorted: emit in sorted order
# Note: leaves with value 0 are skipped by select_sorted
def pred_fn(d, x, i, E):
    # Keep all entries (pred will be checked by select_sorted)
    # Actually, we want to emit only if x != 0
    return R.not0(d, x)

def emit_fn(d, x, i, E):
    # Unpack the key and return (min_c, max_c, weight)
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

        # Reduce by key to group and sum
        grouped = b.call(rk, list=edges_with_c, L=d3)

        # Select sorted to filter and emit in order
        # For the depth of the pair-key trie, use n * 2 as upper bound
        # (since each key is pack(min_c, max_c) where c_i < n)
        pair_depth = R.depth_for(P, b, b.op(n2, "*", 2))
        return b.call(sel, t=grouped, L=pair_depth, E=0)  # E is not used

    return d.branch(n, empty, nonempty, c_copy, edges)

P.prog("t5_rewrite_weighted", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("wrote net.hvm")
