"""t5_rewrite_collapsed: count edges collapsed by clustering rewrite.

Input: clustering c (list of canonical IDs) and edges (list of pairs).
Output: number of edges that disappear as self-loops or duplicates.
"""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, EDGE, TUP, INF, LIST
from genome.lib import recipes as R

P = Program()

# Recipe instances
lc = R.list_length_and_copy(P, "lc", EDGE)
lc_num = R.list_length_and_copy(P, "lc_num", NUM)
ct = R.list_to_trie(P, "ct", NUM)
lk = R.lookup_many(P, "lk", EDGE, lambda d, u, v: (u, v), nkeys=2)

def keyval(d, u, v, cu, cv):
    min_c, max_c = R.min2(d, cu, cv)
    pair_key = R.pack(d, min_c, max_c, 12)
    return pair_key

rk = R.reduce_by_key(P, "rk", TUP(NUM, NUM, NUM, NUM), keyval, "set1")
# For set1, a leaf is 0 if the key was never seen, and 1 if seen. Count only the 1s.
ct_count = R.count_where_trie(P, "cct", lambda d, x, i, e: x, env=NUM)
lg = P.lg()

def prog(d, c, es):
    n, c_copy = d.call(lc_num, list=c)

    def empty_case(b, c_copy, es):
        b.erase(c_copy, es)
        return 0

    def nonempty_case(b, nm1, c_copy, es):
        nm1a, nm1b = b.fanout(nm1, 2)
        b.erase(nm1b)

        n_edges, edges_copy = b.call(lc, list=es)

        L_c = b.call(lg, x=nm1a)
        L1, L2, L3, L4 = b.fanout(L_c, 4)

        c_trie = b.call(ct, list=c_copy, L=L1)

        L2a, L2b = b.fanout(L2, 2)
        b.erase(L2b)
        edges_with_vals = b.call(lk, list=edges_copy, V=c_trie, L=L2a)

        L3a, L3b = b.fanout(L3, 2)
        b.erase(L3b)
        dedup_trie = b.call(rk, list=edges_with_vals, L=L3a)

        n_distinct = b.call(ct_count, t=dedup_trie, L=L4, E=0)

        return b.op(n_edges, "-", n_distinct)

    return d.branch(n, empty_case, nonempty_case, c_copy, es)

P.prog("t5_rewrite_collapsed", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
