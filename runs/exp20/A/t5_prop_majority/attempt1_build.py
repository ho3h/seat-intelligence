import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, TRIE, INF, TUP

def build():
    P = Program()

    lg = P.lg()
    hadd = P.update("hadd", "add")
    const_trie = P.const_trie("z0", 0)

    def fold_freq(d, count, value, acc):
        max_count, best_value = d.split(acc)
        c1, c2, c3 = d.fanout(count, 3)
        v1, v2 = d.fanout(value, 2)
        m1, m2, m3 = d.fanout(max_count, 3)
        b1, b3 = d.fanout(best_value, 2)

        greater = d.op(c1, ">", m1)
        equal = d.op(c2, "=", m2)
        smaller = d.op(v1, "<", b1)
        equal_smaller = d.op(equal, "&", smaller)
        should_update = d.op(greater, "|", equal_smaller)

        def zero_case(b, m3, b3, c3, v2):
            b.erase(c3, v2)
            return (m3, b3)

        def nonzero_case(b, _, m3, b3, c3, v2):
            b.erase(_, m3, b3)
            return (c3, v2)

        return d.branch(should_update,
            zero_case, nonzero_case,
            m3, b3, c3, v2
        )

    fold_freq_prim = P.fold("fold_freq", fold_freq, acc=TUP(NUM, NUM), index=True)

    def step_attrs(d, L, k, key_target, freq_trie, node, key_attr, value_attr):
        L1, L2 = d.fanout(L, 2)
        k1, k2 = d.fanout(k, 2)
        key_t1, key_t2 = d.fanout(key_target, 2)
        d.erase(node, k1)

        match_key = d.op(key_attr, "=", key_t1)

        freq_trie2 = d.branch(match_key,
            lambda b, ft, va, l: (b.erase(va, l), ft)[1],
            lambda b, cm1, ft, va, l: (b.erase(cm1), b.call(hadd, t=ft, k=va, L=l, P=1))[1],
            freq_trie, value_attr, L1
        )

        return L2, k2, key_t2, freq_trie2

    def fin_attrs(d, L, k, key_target, freq_trie):
        d.erase(L, k, key_target)
        return freq_trie

    stream_attrs = P.stream("wa", step_attrs, fin_attrs,
                           state=[("L", DEPTH), ("k", NUM), ("key_target", NUM), ("freq_trie", TRIE(NUM))],
                           elem=TUP(NUM, NUM, NUM))

    def prog(d, k, key, c, attrs):
        d.erase(c)

        large = d.op(0, "-", 1)
        L = d.call(lg, x=large)

        L1, L2, L3 = d.fanout(L, 3)

        freq_init = d.call(const_trie, L=L1)
        freq_final = d.call(stream_attrs, list=attrs, init=(L2, k, key, freq_init))

        result = d.call(fold_freq_prim, t=freq_final, L=L3, acc=(0, INF))
        max_c, best_v = d.split(result)

        is_zero = d.op(max_c, "=", 0)

        return d.branch(is_zero,
            lambda b, bv: (b.erase(bv), INF)[1],
            lambda b, cm1, bv: (b.erase(cm1), bv)[1],
            best_v
        )

    P.prog("t5_prop_majority", prog)
    P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))

if __name__ == "__main__":
    build()
