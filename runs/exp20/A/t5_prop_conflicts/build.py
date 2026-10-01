#!/usr/bin/env python3
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib.glue import Program, NUM, DEPTH, TRIE, WEDGE

P = Program()
zeros = P.const_trie("z0", 0)
inc = P.update("dinc", "inc")
reduce_gt1 = P.reduce("rgt1", lambda d, x: d.op(x, ">", 1), "+")
get_prim = P.get("gt")

def step_count(d, L, L_c, c_trie, result_trie, node, key, value):
    L1, L2, L3 = d.fanout(L, 3)
    cluster_id = d.call(get_prim, t=c_trie, k=node, L=L_c)
    idx = d.op(cluster_id, "<<", 8)
    idx = d.op(idx, "|", key)
    result_trie_new = d.call(inc, t=result_trie, k=idx, L=L1)
    d.erase(value)
    return L2, L3, c_trie, result_trie_new

def fin_count(d, L, L_c, c_trie, result_trie):
    L1, L2 = d.fanout(L, 2)
    d.erase(L_c, c_trie)
    return d.call(reduce_gt1, t=result_trie, L=L1)

stream_count = P.stream("cnt", step_count, fin_count,
    state=[("L", DEPTH), ("L_c", DEPTH), ("c", TRIE(NUM)), ("t", TRIE(NUM))],
    elem=WEDGE)

def prog(d, c_list, attrs_list):
    d.erase(c_list)
    L_init = 16
    L1, L2, L3 = d.fanout(L_init, 3)
    c_trie = d.call(zeros, L=L1)
    result_trie_init = d.call(zeros, L=L3)
    return d.call(stream_count, list=attrs_list, init=(L2, L_init, c_trie, result_trie_init))

P.prog("t5_prop_conflicts", prog)
P.write(os.path.join(D, "net.hvm"))
print("Wrote net.hvm")
