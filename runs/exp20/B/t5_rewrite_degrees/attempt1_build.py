"""t5_rewrite_degrees: degrees of clusters in the merged graph."""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, EDGE, INF
from genome.lib import recipes as R

P = Program()

# Primitives
lg = P.lg()
const_zero = P.const_trie("z0", 0)
inc = P.update("dinc", "inc")
to_list = P.to_list("tl")

# Recipes
lc = R.list_length_and_copy(P, "lc", NUM)
ct = R.list_to_trie(P, "ct", NUM)
lk = R.lookup_many(P, "lk", EDGE, lambda d, u, v: (u, v), nkeys=2)

# Filter edges where c[u] != c[v]
fil = R.filter_in_order(P, "fil", TUP(NUM, NUM, NUM, NUM),
                        lambda d, u, v, cu, cv: R.not0(d, d.op(cu, "!", cv)))

# Reduce to distinct normalized edges
# For each edge (u, v, cu, cv), pack (min(cu,cv), max(cu,cv)) as the key with bits=L
# Need to pass L through environment
rb = R.reduce_by_key(P, "rb", TUP(NUM, NUM, NUM, NUM),
                     lambda d, u, v, cu, cv, L: R.pack(d, *R.min2(d, cu, cv), L),
                     combine="set1", env=NUM)

# Unpack edges and select sorted
# pred: keep all leaves (since we already filtered in reduce_by_key)
# emit: unpack the key to get (a, b)
sel = R.select_sorted(P, "sel",
                      lambda d, x, i, L: 1,  # pred: keep all leaves
                      lambda d, x, i, L: R.unpack(d, i, L),  # emit: unpack (min, max)
                      leaf_kind=NUM, env=NUM)

def prog(d, c_list, es):
    # Get length of c
    n, c = d.call(lc, list=c_list)

    # Handle empty case: if n == 0, output []
    def empty(b, c, es):
        b.erase(c, es)
        return b.nil()

    def nonempty(b, nm1, c, es):
        # Compute n and depth: L = lg(n-1)
        nm1a, nm1b = b.fanout(nm1, 2)
        n_val = b.op(nm1b, "+", 1)
        L = b.call(lg, x=nm1a)

        # Get c as a trie
        L1, L2, L3, L4, L5, L6, L7, L8 = b.fanout(L, 8)
        ct_c = b.call(ct, list=c, L=L1)

        # Look up c[u] and c[v] for each edge: list of (u, v, c[u], c[v])
        edges_c = b.call(lk, list=es, V=ct_c, L=L2)

        # Filter edges where c[u] != c[v]
        filtered = b.call(fil, list=edges_c)

        # Reduce to distinct normalized edges, packing (min(cu,cv), max(cu,cv)) as key
        # Pass L as environment for packing
        distinct = b.call(rb, list=filtered, L=L3, E=L4)

        # Unpack edges using select_sorted: get (a, b) for each distinct edge
        unpacked = b.call(sel, t=distinct, L=L5, E=L6)

        # Count neighbors per cluster using a stream walker
        def count_step(d, H, L, a, b):
            L1, L2, L3 = d.fanout(L, 3)
            H1 = d.call(inc, t=H, k=a, L=L1)
            H2 = d.call(inc, t=H1, k=b, L=L2)
            return H2, L3

        def count_fin(d, H, L):
            d.erase(L)
            return H

        count_walker = P.stream("count_walker", count_step, count_fin,
                                state=[("H", TRIE(NUM)), ("L", DEPTH)], elem=EDGE)

        # Initialize counter trie and run walker
        L7a, L7b = b.fanout(L7, 2)
        H = b.call(count_walker, list=unpacked, init=(b.call(const_zero, L=L7a), L7b))

        # Convert to output list: list of first n degrees
        return b.call(to_list, t=H, L=L8, n=n_val)

    return d.branch(n, empty, nonempty, c, es)

P.prog("t5_rewrite_degrees", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("wrote net.hvm")
