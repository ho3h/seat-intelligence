"""
Cycle detection in a pointer list using pointer jumping and multicast lookup.

Algorithm:
1. Apply pointer_jump to compress pointers (256 jumps)
2. After many jumps, nodes either reach fixed points (roots) or cycle
3. Check if p[o[i]] == o[i] for each o[i]
   - If all match, no cycles (all at fixed points)
   - If any differs, there's a cycle
"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, EDGE, WEDGE, INF
from genome.lib import recipes as R

P = Program()

# Create recipe instances
pj = R.pointer_jump(P, "pj", rounds=8)  # list[num] -> list[num]
lc = R.list_length_and_copy(P, "lc", NUM, copies=2)  # list[num] -> (n, c1, c2)
tri = R.list_to_trie(P, "tri", NUM)  # (list[num], L) -> trie[num]
lk = R.lookup_many(P, "lk", NUM, lambda d, oi: oi, nkeys=1)  # (list[num], trie[num], L) -> list[(num, num)]
cw = R.count_where(P, "cw", EDGE, lambda d, oi, p_oi: d.op(oi, "!", p_oi), env=None)  # list[(num, num)] -> count
lg = P.lg()  # num -> depth

def prog(d, p):
    """
    Detect if the pointer list p contains a cycle (of length >= 2).
    Returns 1 if a cycle exists, 0 otherwise.
    """
    # Extract length and get 2 copies of the list
    n, p_copy1, p_copy2 = d.call(lc, list=p)

    def empty(b, p_copy1, p_copy2):
        # n == 0: empty list has no cycles
        b.erase(p_copy1, p_copy2)
        return 0

    def nonempty(b, nm1, p_copy1, p_copy2):
        # n > 0: use pointer jumping and multicast lookup
        # nm1 = n - 1

        # Compute log(n-1) for trie depth
        L = b.call(lg, x=nm1)
        L1, L2 = b.fanout(L, 2)

        # Apply pointer_jump to get o (after 256 jumps)
        o = b.call(pj, list=p_copy1)

        # Convert p_copy2 to a trie for lookup
        p_trie = b.call(tri, list=p_copy2, L=L1)

        # Look up p[o[i]] for each o[i]
        # Returns list of (o[i], p[o[i]]) pairs
        checked = b.call(lk, list=o, V=p_trie, L=L2)

        # Count how many pairs have o[i] != p[o[i]]
        # If any node is not at a fixed point, there's a cycle
        count = b.call(cw, list=checked)

        # Return 1 if count > 0 (cycle found), else 0
        return b.select(count, 1, 0)

    return d.branch(n, empty, nonempty, p_copy1, p_copy2)

P.prog("t5_rewrite_sameas_cycle", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Built net.hvm")
