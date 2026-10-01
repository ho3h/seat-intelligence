"""
t5_decide_drop_known: Filter candidates - using recipes with proper empty handling.
"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TUP, EDGE, WEDGE, INF
from genome.lib import recipes as R

P = Program()

lc_known = R.list_length_and_copy(P, "lc_known", EDGE, key=lambda d, u, v: R.max2(d, u, v))
rk = R.reduce_by_key(P, "rk", EDGE, lambda d, u, v: R.pack(d, u, v, 12), combine="set1")
lk = R.lookup_many(P, "lk", WEDGE, lambda d, u, v, s: R.pack(d, u, v, 12), nkeys=1)

def prog(d, known, cands):
    n_known, mx_known, known_copy = d.call(lc_known, list=known)
    d.erase(n_known)  # Not needed

    # Compute proper depth for known pairs (handles empty case)
    max_id = R.max2(d, mx_known, 0)
    L = R.depth_for(P, d, d.op(max_id, "+", 1))
    L_a, L_b = d.fanout(L, 2)

    # Build known trie
    known_trie = d.call(rk, list=known_copy, L=L_a)

    # Lookup pairs in cands (returns (u, v, s, found))
    cands_marked = d.call(lk, list=cands, V=known_trie, L=L_b)

    # Filter to keep only where found == 0
    fc = R.filter_in_order(P, "fc", TUP(NUM, NUM, NUM, NUM),
                            lambda d2, u, v, s, found: R.not0(d2, d2.op(1, "-", found)))
    filtered = d.call(fc, list=cands_marked)

    # Extract (u, v, s) from (u, v, s, found)
    def step_extract(b, result, u, v, s, found):
        b.erase(found)
        return b.cons((u, v, s), result)

    def fin_extract(b, result):
        return result

    w_extract = P.stream("w_extract", step_extract, fin_extract,
                         state=[("result", LIST(WEDGE))],
                         elem=TUP(NUM, NUM, NUM, NUM))

    result = d.call(w_extract, list=filtered, init=d.nil())
    return result

P.prog("t5_decide_drop_known", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
