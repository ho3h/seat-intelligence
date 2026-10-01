"""t5_rewrite_degrees: degrees of clusters in the merged graph."""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, EDGE, INF
from genome.lib import recipes as R

P = Program()

# Primitives
const_zero = P.const_trie("z0", 0)
inc = P.update("dinc", "inc")
to_list = P.to_list("tl")

# Recipes
lc = R.list_length_and_copy(P, "lc", NUM)
ct = R.list_to_trie(P, "ct", NUM)
lk = R.lookup_many(P, "lk", EDGE, lambda d, u, v: (u, v), nkeys=2)
fil = R.filter_in_order(P, "fil", TUP(NUM, NUM, NUM, NUM),
                        lambda d, u, v, cu, cv: R.not0(d, d.op(cu, "!", cv)))
rb = R.reduce_by_key(P, "rb", TUP(NUM, NUM, NUM, NUM),
                     lambda d, u, v, cu, cv, L: R.pack(d, *R.min2(d, cu, cv), L),
                     combine="set1", env=NUM)
sel = R.select_sorted(P, "sel",
                      lambda d, x, i, E: 1,
                      lambda d, x, i, E: R.unpack(d, i, E),
                      leaf_kind=NUM, env=NUM)

def prog(d, c_list, es):
    n, c = d.call(lc, list=c_list)

    def empty(b, c, es):
        b.erase(c, es)
        return b.nil()

    def nonempty(b, nm1, c, es):
        n_val = b.op(nm1, "+", 1)
        n_depth, n_out = b.fanout(n_val, 2)
        L = R.depth_for(P, b, n_depth)

        L1, L2, L3, L4, L5, L6, L7, L8, L9 = b.fanout(L, 9)

        ct_c = b.call(ct, list=c, L=L1)
        edges_c = b.call(lk, list=es, V=ct_c, L=L2)
        filtered = b.call(fil, list=edges_c)
        distinct = b.call(rb, list=filtered, L=L3, E=L4)
        unpacked = b.call(sel, t=distinct, L=L5, E=L6)

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

        H = b.call(count_walker, list=unpacked, init=(b.call(const_zero, L=L7), L8))
        return b.call(to_list, t=H, L=L9, n=n_out)

    return d.branch(n, empty, nonempty, c, es)

P.prog("t5_rewrite_degrees", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("wrote net.hvm")
