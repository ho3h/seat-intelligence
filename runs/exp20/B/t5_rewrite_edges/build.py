import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, EDGE, WEDGE, INF
from genome.lib import recipes as R

P = Program()

# Create recipe instances
# Step 1: Get length and copy of clustering list
lc = R.list_length_and_copy(P, "lc", NUM)

# Step 2: Convert clustering list to trie
ct = R.list_to_trie(P, "ct", NUM)

# Step 3: Look up c[u] and c[v] for each edge
# This returns (u, v, c[u], c[v])
lk = R.lookup_many(P, "lk", EDGE, lambda d, u, v: (u, v), nkeys=2)

# Step 4: Filter out self-loops (where c[u] == c[v])
filt = R.filter_in_order(P, "filt", TUP(NUM, NUM, NUM, NUM),
                         lambda d, u, v, cu, cv: d.op(1, "-", d.op(cu, "=", cv)))

# Step 5: Reduce by key to deduplicate edges
# Key is pack(min(cu, cv), max(cu, cv), B)
def keyval(d, u, v, cu, cv, B):
    minx, maxx = R.min2(d, cu, cv)
    return R.pack(d, minx, maxx, B)

rk = R.reduce_by_key(P, "rk", TUP(NUM, NUM, NUM, NUM), keyval, "set1", env=NUM)

# Step 6: Select sorted to output sorted (x, y) pairs
def emit(d, x, i, B):
    return R.unpack(d, i, B)

sel = R.select_sorted(P, "sel", lambda d, x, i, B: x, emit)

def prog(d, c, es):
    # Get length and copy of c
    n, c_copy = d.call(lc, list=c)

    # Compute bit depth for vertex ids
    L = R.depth_for(P, d, n)
    L1, L2, L3, L4, L5, L6 = d.fanout(L, 6)

    # Convert c to trie for fast lookup
    c_trie = d.call(ct, list=c_copy, L=L1)

    # Look up c[u] and c[v] for each edge
    # This gives us (u, v, c[u], c[v])
    looked_up = d.call(lk, list=es, V=c_trie, L=L2)

    # Filter out self-loops (c[u] == c[v])
    filtered = d.call(filt, list=looked_up)

    # Reduce by key to deduplicate
    # Use L3 as the bit depth environment for packing
    # Pair-key depth is 2*L (for keys from packing two L-bit values)
    pair_L1 = d.as_depth(d.op(L4, "*", 2))
    pair_L2 = d.as_depth(d.op(L5, "*", 2))
    H = d.call(rk, list=filtered, L=pair_L1, E=L6)

    # Select sorted to output pairs in order
    return d.call(sel, t=H, L=pair_L2, E=L3)

P.prog("t5_rewrite_edges", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
