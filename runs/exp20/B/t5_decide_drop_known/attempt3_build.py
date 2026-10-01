"""
t5_decide_drop_known: Filter candidates by removing pairs that exist in known list.
Condition B: Stream-based with peek for trie queries.
"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, EDGE, WEDGE, INF

P = Program()

# Primitives
const_trie = P.const_trie("z0", 0)
hadd = P.update("hadd", "add")
peek_prim = P.update("pk", "peek")

def prog(d, known, cands):
    # Step 1: Build known set
    def step_known(b, L, H, u, v):
        L1, L2 = b.fanout(L, 2)
        key = b.op(b.op(u, "<<", 12), "|", v)
        H2 = b.call(hadd, t=H, k=key, L=L1, P=1)
        return L2, H2

    def fin_known(b, L, H):
        b.erase(L)
        return H

    w_known = P.stream("w_known", step_known, fin_known,
                       state=[("L", DEPTH), ("H", TRIE(NUM))],
                       elem=EDGE)

    # Step 2: Filter cands
    def step_filter(b, L, H, result, u, v, s):
        L1, L2 = b.fanout(L, 2)
        u_a, u_b = b.fanout(u, 2)
        v_a, v_b = b.fanout(v, 2)
        key = b.op(b.op(u_a, "<<", 12), "|", v_a)

        # Look up in trie with peek (returns value and trie copy)
        found, H2 = b.call(peek_prim, t=H, k=key, L=L1)

        # If not found (== 0), append
        def keep(b2, u, v, s, result, H2):
            triple = (u, v, s)
            new_result = b2.cons(triple, result)
            return new_result, H2

        def drop(b2, f, u, v, s, result, H2):
            b2.erase(u, v, s, f)
            return result, H2

        new_result, H3 = b.branch(found, keep, drop, u_b, v_b, s, result, H2)
        return L2, H3, new_result

    def fin_filter(b, L, H, result):
        b.erase(L, H)
        return result

    w_cands = P.stream("w_cands", step_filter, fin_filter,
                       state=[("L", DEPTH), ("H", TRIE(NUM)), ("result", LIST(WEDGE))],
                       elem=WEDGE)

    # Build known set
    L = d.as_depth(24)
    L_a, L_b, L_c = d.fanout(L, 3)
    H_init = d.call(const_trie, L=L_a)
    known_trie = d.call(w_known, list=known, init=(L_b, H_init))

    # Filter cands with known trie
    result = d.call(w_cands, list=cands, init=(L_c, known_trie, d.nil()))

    return result

P.prog("t5_decide_drop_known", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
