"""Build script for t5_prop_majority (condition B): majority merge of one property."""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, INF
from genome.lib import recipes as R

P = Program()

# Filter attrs by attribute key
f1 = R.filter_in_order(P, "f1", TUP(NUM, NUM, NUM), lambda d, node, attr_key, value, key: d.op(attr_key, "=", key), env=NUM)

# Look up c[node] for each attribute
lk = R.lookup_many(P, "lk", TUP(NUM, NUM, NUM), lambda d, node, attr_key, value: node, nkeys=1)

# Filter by c[node] == k
def keyval_fn(d, node, attr_key, value, c_node, k):
    c_match = d.op(c_node, "=", k)
    # Need to fanout c_match for both branches
    c_match_1, c_match_2 = d.fanout(c_match, 2)
    # Return (value, 1) if c_match else (0, 0)
    v = d.select(c_match_1, value, 0)
    cnt = d.select(c_match_2, 1, 0)
    return (v, cnt)

rk = R.reduce_by_key(P, "rk", TUP(NUM, NUM, NUM, NUM), keyval_fn, combine="add", env=NUM)

# Find argmax: returns (count, value_index)
def value_fn(d, count, i, env):
    count1, count2 = d.fanout(count, 2)
    ok = R.not0(d, count1)
    return (ok, count2)

am = R.argmax_first_trie(P, "am", value_fn)

# Get length and copy of c, build trie from c
lc = R.list_length_and_copy(P, "lc", NUM)
tri = R.list_to_trie(P, "ct", NUM)

def prog(d, k, key, c, attrs):
    # Get length and copy of c
    n, c_copy = d.call(lc, list=c)

    # Branch on n
    def empty_n(b, k, key, c_copy, attrs):
        b.erase(k, key, c_copy, attrs)
        return INF

    def nonempty_n(b, n_nm1, k, key, c_copy, attrs):
        # Reconstruct n from n_nm1
        n = b.op(n_nm1, "+", 1)

        # Compute depth for c trie
        L_c = R.depth_for(P, b, n)
        L_c1, L_c2 = b.fanout(L_c, 2)

        # Compute depth for histogram trie (keys are attribute values, up to 16777215)
        # We need a large depth to accommodate any value
        L_hist = R.depth_for(P, b, 16777216)

        # Build trie from c
        c_trie = b.call(tri, list=c_copy, L=L_c1)

        # Filter attrs by attr_key == key
        k1, k2 = b.fanout(key, 2)
        filtered_attrs = b.call(f1, list=attrs, E=k1)

        # Look up c[node] for each filtered attribute
        attrs_with_c = b.call(lk, list=filtered_attrs, V=c_trie, L=L_c2)

        # Apply reduce_by_key to count values where c[node] == k
        k3, k4, k5 = b.fanout(k, 3)
        L_hist1, L_hist2 = b.fanout(L_hist, 2)
        histogram = b.call(rk, list=attrs_with_c, L=L_hist1, E=k3)

        # Find argmax (returns mx=count, idx=value)
        mx, idx = b.call(am, t=histogram, L=L_hist2, E=0)

        # Return idx if valid (idx != 16777215), otherwise INF
        b.erase(mx, k2, k4, k5)
        idx1, idx2 = b.fanout(idx, 2)
        is_valid = b.op(idx1, "!", 16777215)
        result = b.select(is_valid, idx2, INF)
        return result

    return d.branch(n, empty_n, nonempty_n, k, key, c_copy, attrs)

P.prog("t5_prop_majority", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("wrote net.hvm")
