"""t5_conflict_count: count violated must-not-link pairs in a clustering."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib.glue import Program, NUM, DEPTH, TRIE, LIST, TUP, INF

def build():
    P = Program()
    lg = P.lg()
    zeros = P.const_trie("z0", 0)
    set_upd = P.update("st", "set")
    peek_upd = P.update("pk", "peek")

    def c_step(d, L, idx, ct, v):
        L1, L2 = d.fanout(L, 2)
        idx1, idx2 = d.fanout(idx, 2)
        ct2 = d.call(set_upd, t=ct, k=idx1, L=L1, P=v)
        idx_new = d.op(idx2, "+", 1)
        return L2, idx_new, ct2

    def c_fin(d, L, idx, ct):
        d.erase(L)
        d.erase(idx)
        return ct

    c_stream = P.stream("c_stream", c_step, c_fin,
                        state=[("L", DEPTH), ("idx", NUM), ("ct", TRIE(NUM))],
                        elem=NUM)

    def mnl_step(d, L, ct, count, a, b):
        L1, L2, L3 = d.fanout(L, 3)
        ca, ct1 = d.call(peek_upd, t=ct, k=a, L=L1)
        cb, ct2 = d.call(peek_upd, t=ct1, k=b, L=L2)
        is_equal = d.op(ca, "=", cb)
        count_new = d.op(count, "+", is_equal)
        return L3, ct2, count_new

    def mnl_fin(d, L, ct, count):
        d.erase(L)
        d.erase(ct)
        return count

    mnl_stream = P.stream("mnl_stream", mnl_step, mnl_fin,
                          state=[("L", DEPTH), ("ct", TRIE(NUM)), ("count", NUM)],
                          elem=TUP(NUM, NUM))

    def prog(d, c, mnl):
        # Compute L from a fixed constant
        # lg(255) = 8, which supports up to 256 elements
        L = d.call(lg, x=255)
        L1, L2, L3 = d.fanout(L, 3)

        # Build trie from c by walking through it
        c_trie_init = d.call(zeros, L=L1)
        c_trie = d.call(c_stream, list=c, init=(L2, 0, c_trie_init))

        # Count violations in mnl by walking through it and looking up in c_trie
        count = d.call(mnl_stream, list=mnl, init=(L3, c_trie, 0))
        return count

    P.prog("t5_conflict_count", prog)
    return P

if __name__ == "__main__":
    P = build()
    path = os.path.join(D, "net.hvm")
    P.write(path)
    print(f"wrote {path}")
