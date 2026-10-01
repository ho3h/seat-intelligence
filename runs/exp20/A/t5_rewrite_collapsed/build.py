#!/usr/bin/env python3
"""
Build script for t5_rewrite_collapsed: count edges collapsed by clustering rewrite.
"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, EDGE, INF

P = Program()

# Primitives
lg = P.lg()
const0 = P.const_trie("z0", 0)
set_val = P.update("upd_set", "set")
peek_val = P.update("pk", "peek")  # Returns (value, trie) without consuming trie
reduce_sum = P.reduce("r_sum", lambda d, x: x, "+")
to_list_prim = P.to_list("tl")

# Walker 1: Count elements in a list
def step_count(d, n, x):
    d.erase(x)
    return d.op(n, "+", 1)

def fin_count(d, n):
    return n

counter = P.stream("counter", step_count, fin_count,
                   state=[("n", NUM)],
                   elem=NUM)

# Walker 2: Build clustering trie from list
# State: (L, i, trie)
def step_build_cluster(d, L, i, trie, c_i):
    L_a, L_b = d.fanout(L, 2)
    i_a, i_b = d.fanout(i, 2)
    trie2 = d.call(set_val, t=trie, k=i_a, L=L_a, P=c_i)
    i_next = d.op(i_b, "+", 1)
    return L_b, i_next, trie2

def fin_build_cluster(d, L, i, trie):
    d.erase(L, i)
    return trie

cluster_builder = P.stream("cluster_builder", step_build_cluster, fin_build_cluster,
                           state=[("L", DEPTH), ("i", NUM), ("trie", TRIE(NUM))],
                           elem=NUM)

# Walker 3: Process edges and build histogram
# State: (L_cluster, c_trie, L_hist, histogram, total)
def step_edges(d, L_cluster, c_trie, L_hist, histogram, total, u, v):
    # Fanout L_cluster since it's used twice (for peeks) and needs to be returned
    L_cluster_a, L_cluster_b, L_cluster_ret = d.fanout(L_cluster, 3)

    # Look up c[u] using peek (returns value and updated trie)
    cu, c_trie2 = d.call(peek_val, t=c_trie, k=u, L=L_cluster_a)

    # Look up c[v] using peek
    cv, c_trie3 = d.call(peek_val, t=c_trie2, k=v, L=L_cluster_b)

    # Fanout for use in multiple places
    # cu is used: for self-loop check, for min/max comparison, for min select, for max select
    cu_cmp, cu_minmax_cmp, cu_min_sel, cu_max_sel = d.fanout(cu, 4)
    # cv is used: for self-loop check, for min/max comparison, for min select, for max select
    cv_cmp, cv_minmax_cmp, cv_min_sel, cv_max_sel = d.fanout(cv, 4)

    # Check if self-loop: cu == cv
    is_self_loop = d.op(cu_cmp, "=", cv_cmp)

    # Compute min and max
    is_cu_less = d.op(cu_minmax_cmp, "<", cv_minmax_cmp)
    is_cu_less_a, is_cu_less_b = d.fanout(is_cu_less, 2)
    min_c = d.select(is_cu_less_a, cu_min_sel, cv_min_sel)
    max_c = d.select(is_cu_less_b, cv_max_sel, cu_max_sel)

    # Encode as key: key = min_c + max_c * 256
    max_c_times_256 = d.op(max_c, "*", 256)
    key = d.op(min_c, "+", max_c_times_256)

    # Update histogram[key] = 1 only if not self-loop
    # Use branch to conditionally update
    # When is_self_loop == 0 (not a self-loop), update; when is_self_loop == 1, skip
    def do_update(b, histogram, key, L_hist_local):
        return b.call(set_val, t=histogram, k=key, L=L_hist_local, P=1)

    def skip_update(b, nm1, histogram, key, L_hist_local):
        b.erase(nm1)
        b.erase(key, L_hist_local)
        return histogram

    # Fanout L_hist since it's used in branch and also returned
    L_hist_branch, L_hist_ret = d.fanout(L_hist, 2)
    # is_self_loop == 0 means not a self-loop, so update; == 1 means skip
    histogram3 = d.branch(is_self_loop, do_update, skip_update, histogram, key, L_hist_branch)

    # Increment total
    total_next = d.op(total, "+", 1)

    return L_cluster_ret, c_trie3, L_hist_ret, histogram3, total_next

def fin_edges(d, L_cluster, c_trie, L_hist, histogram, total):
    d.erase(L_cluster, c_trie)
    # Fanout L_hist since it's used for erase intention but also for reduce
    L_hist_a, L_hist_b = d.fanout(L_hist, 2)
    # Count distinct edges (number of 1s in histogram) using reduce
    distinct = d.call(reduce_sum, t=histogram, L=L_hist_a)
    # Erase L_hist_b since we don't need it anymore
    d.erase(L_hist_b)
    # Compute and return result = total - distinct
    result = d.op(total, "-", distinct)
    return result

edge_processor = P.stream("edge_processor", step_edges, fin_edges,
                          state=[("L_cluster", DEPTH), ("c_trie", TRIE(NUM)),
                                 ("L_hist", DEPTH), ("histogram", TRIE(NUM)),
                                 ("total", NUM)],
                          elem=EDGE)

# Main program
def prog(d, c_list, edges_list):
    # Use a fixed L=16 which works for the maximum inputs (n=144)
    # Encoding edges as key = min_c + max_c * 256
    # Max key = 143 + 144*256 = 36863, which requires L >= 16
    # This avoids needing to count c_list
    L_fixed = 16

    # Build clustering trie from c_list
    c_trie = d.call(cluster_builder, list=c_list, init=(L_fixed, 0, d.call(const0, L=L_fixed)))

    # Process edges using the clustering trie
    result = d.call(edge_processor, list=edges_list,
                    init=(L_fixed, c_trie, L_fixed, d.call(const0, L=L_fixed), 0))

    return result

P.prog("t5_rewrite_collapsed", prog)
P.write(os.path.join(os.path.dirname(__file__), "net.hvm"))
