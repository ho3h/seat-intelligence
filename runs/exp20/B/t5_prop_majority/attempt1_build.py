"""Build script for t5_prop_majority (condition B): majority merge of one property."""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, INF
from genome.lib import recipes as R

P = Program()

# Create recipe instances
lc = R.list_length_and_copy(P, "lc", NUM)
tri = R.list_to_trie(P, "ct", NUM)
lk = R.lookup_many(P, "lk", TUP(NUM, NUM, NUM), lambda d, node, attr_key, value: node, nkeys=1)

# Filter and count: reduce_by_key counts values where c[node] == k and attr_key == key
# Environment packs k and key: (k << 2) | key
def keyval_fn(d, node, attr_key, value, c_node, k_key_packed):
    k_key_1, k_key_2 = d.fanout(k_key_packed, 2)
    k_unpacked = d.op(k_key_1, ">>", 2)
    key_unpacked = d.op(k_key_2, "&", 3)

    k_match = d.op(c_node, "=", k_unpacked)
    key_match = d.op(attr_key, "=", key_unpacked)
    both_match = d.op(k_match, "&", key_match)

    # Need to fanout both_match for both branches
    both_match_1, both_match_2 = d.fanout(both_match, 2)

    # Return (value, 1) if conditions match, (0, 0) otherwise
    v = d.select(both_match_1, value, 0)
    cnt = d.select(both_match_2, 1, 0)
    return (v, cnt)

rk = R.reduce_by_key(P, "rk", TUP(NUM, NUM, NUM, NUM), keyval_fn, combine="add", env=NUM)

# Find argmax: returns (count, value_index)
def value_fn(d, count, i, env):
    count1, count2 = d.fanout(count, 2)
    ok = R.not0(d, count1)
    return (ok, count2)

am = R.argmax_first_trie(P, "am", value_fn)

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
        L_c1, L_c2, L_c3 = b.fanout(L_c, 3)

        # Build trie from c
        c_trie = b.call(tri, list=c_copy, L=L_c1)

        # Look up c[node] for each attribute
        attrs_with_c = b.call(lk, list=attrs, V=c_trie, L=L_c2)

        # Pack k and key into a single environment number
        k1, k2, k3 = b.fanout(k, 3)
        key1, key2 = b.fanout(key, 2)
        k_key_packed = b.op(b.op(k1, "<<", 2), "|", key1)

        # Apply reduce_by_key to count values
        histogram = b.call(rk, list=attrs_with_c, L=L_c3, E=k_key_packed)

        # Find argmax (returns mx=count, idx=value)
        L_for_argmax = R.depth_for(P, b, 16777216)
        mx, idx = b.call(am, t=histogram, L=L_for_argmax, E=0)

        # Return idx if valid (idx != 16777215), otherwise INF
        b.erase(mx, k2, k3, key2)
        idx1, idx2 = b.fanout(idx, 2)
        is_valid = b.op(idx1, "!", 16777215)
        result = b.select(is_valid, idx2, INF)
        return result

    return d.branch(n, empty_n, nonempty_n, k, key, c_copy, attrs)

P.prog("t5_prop_majority", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("wrote net.hvm")
