"""t5_rewrite_collapsed: count edges collapsed by clustering rewrite."""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, EDGE, TUP, INF, LIST
from genome.lib import recipes as R

P = Program()

lc = R.list_length_and_copy(P, "lc", EDGE)
lc_num = R.list_length_and_copy(P, "lc_num", NUM)
ct = R.list_to_trie(P, "ct", NUM)
lk = R.lookup_many(P, "lk", EDGE, lambda d, u, v: (u, v), nkeys=2)

def keyval(d, u, v, cu, cv):
    d.erase(u, v)
    cu1, cu2 = d.fanout(cu, 2)
    cv1, cv2 = d.fanout(cv, 2)
    min_c, max_c = R.min2(d, cu1, cv1)
    pair_key = R.pack(d, min_c, max_c, 12)
    # Only include non-self-loops
    is_self = d.op(cu2, "=", cv2)
    not_self = d.op(1, "-", is_self)
    # Return (key, not_self): only non-self-loops contribute
    return pair_key, not_self

rk = R.reduce_by_key(P, "rk", TUP(NUM, NUM, NUM, NUM), keyval, "add")
# Count leaves where x >= 1 (at least one non-self-loop edge with this key)
ct_count = R.count_where_trie(P, "cct", lambda d, x, i, e: R.not0(d, x), env=NUM)
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
        L1, L2, L3 = b.fanout(L_c, 3)
        c_trie = b.call(ct, list=c_copy, L=L1)
        L2a, L2b = b.fanout(L2, 2)
        b.erase(L2b)
        edges_with_vals = b.call(lk, list=edges_copy, V=c_trie, L=L2a)
        dedup_trie = b.call(rk, list=edges_with_vals, L=L3)
        n_distinct = b.call(ct_count, t=dedup_trie, L=b.as_depth(14), E=0)
        return b.op(n_edges, "-", n_distinct)

    return d.branch(n, empty_case, nonempty_case, c_copy, es)

P.prog("t5_rewrite_collapsed", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
