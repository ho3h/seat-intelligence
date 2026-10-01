#!/usr/bin/env python3
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, INF
from genome.lib import recipes as R

P = Program()

lc = R.list_length_and_copy(P, "lc", NUM)
lc2 = R.list_length_and_copy(P, "lc2", TUP(NUM, NUM, NUM))
tri = R.list_to_trie(P, "tri", NUM)
lk = R.lookup_many(P, "lk", TUP(NUM, NUM, NUM),
                   lambda d, n, k, v: n, nkeys=1)

def keyval_conflict(d, node, key, val, cluster, env):
    ck_shifted = d.op(cluster, "<<", 2)
    ck = d.op(ck_shifted, "|", key)
    return ck, val

def combine_conflict(d, leaf, v):
    leaf_a, leaf_b, leaf_c = d.fanout(leaf, 3)
    is_inf = d.op(leaf_a, "=", INF)
    is_same = d.op(leaf_b, "=", v)
    not_same = d.op(1, "-", is_same)
    conflict = d.op(is_inf, "|", not_same)
    return d.select(conflict, INF, leaf_c)

rk_conflict = R.reduce_by_key(P, "rk", TUP(NUM, NUM, NUM, NUM),
                              keyval_conflict,
                              combine=combine_conflict,
                              env=NUM)

cnt = R.count_where_trie(P, "cnt",
                         lambda d, x, i, n: d.op(x, "=", INF),
                         env=NUM)

def prog(d, c, attrs):
    n_c, c_copy = d.call(lc, list=c)
    n_attrs, attrs_copy = d.call(lc2, list=attrs)
    d.erase(n_attrs)

    def empty_c(b, c_copy, attrs_copy):
        b.erase(c_copy)
        b.erase(attrs_copy)
        return 0

    def nonempty_c(b, nm1_c, c_copy, attrs_copy):
        n_c_actual = b.op(nm1_c, "+", 1)
        n_c_1, n_c_2, n_c_3 = b.fanout(n_c_actual, 3)

        Lc_full = R.depth_for(P, b, n_c_1)
        Lc1, Lc2, Lc3 = b.fanout(Lc_full, 3)

        c_trie = b.call(tri, list=c_copy, L=Lc1)
        looked_up = b.call(lk, list=attrs_copy, V=c_trie, L=Lc2)

        n_c_shifted = b.op(n_c_2, "<<", 2)
        Lck_full = R.depth_for(P, b, n_c_shifted)
        Lck1, Lck2 = b.fanout(Lck_full, 2)

        conflict_trie = b.call(rk_conflict, list=looked_up, L=Lck1, E=Lc3)
        result = b.call(cnt, t=conflict_trie, L=Lck2, E=n_c_3)

        return result

    return d.branch(n_c, empty_c, nonempty_c, c_copy, attrs_copy)

P.prog("t5_prop_conflicts", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Wrote net.hvm")
