"""Build t5_rewrite_weighted: weighted edge rewrite net using glue API."""
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, NUM, TRIE, LIST, WEDGE, MCQ

P = Program()

# Primitives
lg = P.lg()
const_zero = P.const_trie("z0", 0)
hadd = P.update("hadd", "add")
mc_empty = P.mc_empty("mcq_empty")
mc_request = P.mc_request("mcq_req")
mc_deliver_keep = P.mc_deliver_keep("mcq_keep")

# Stream to build clustering trie from list
def c_step(d, idx, c_trie, c_elem):
    idx1, idx2, idx3 = d.fanout(idx, 3)
    L = d.call(lg, x=idx1)
    c_new = d.call(hadd, t=c_trie, k=idx2, L=L, P=c_elem)
    idx_next = d.op(idx3, "+", 1)
    return idx_next, c_new

def c_fin(d, idx, c_trie):
    d.erase(idx)
    return c_trie

c_stream = P.stream("c_stream", c_step, c_fin,
                   state=[("idx", NUM), ("c_trie", TRIE(NUM))],
                   elem=NUM)

# Stream to process edges
def e_step(d, acc_trie, req_q, u, v, w):
    # Request c[u] and c[v]
    cu, req_q1 = d.call(mc_request, q=req_q, k=u, L=18)
    cv, req_q2 = d.call(mc_request, q=req_q1, k=v, L=18)

    # Fanout for reuse
    cu1, cu2, cu3 = d.fanout(cu, 3)
    cv1, cv2, cv3 = d.fanout(cv, 3)

    # Compute min and max
    cu_lt_cv = d.op(cu1, "<", cv1)
    cond1, cond2 = d.fanout(cu_lt_cv, 2)

    x = d.select(cond1, cu2, cv2)
    y = d.select(cond2, cv3, cu3)

    # Combine key
    x_times_256 = d.op(x, "*", 256)
    key = d.op(x_times_256, "+", y)

    # Update accumulator
    acc_new = d.call(hadd, t=acc_trie, k=key, L=18, P=w)

    return acc_new, req_q2

def e_fin(d, acc_trie, req_q):
    d.erase(req_q)
    return acc_trie

e_stream = P.stream("e_stream", e_step, e_fin,
                    state=[("acc_trie", TRIE(NUM)), ("req_q", MCQ)],
                    elem=WEDGE)

# Fold to build output list
def out_fold_leaf(d, weight, idx, acc_list):
    idx1, idx2 = d.fanout(idx, 2)
    x = d.op(idx1, ">>", 8)
    y = d.op(idx2, "&", 255)
    triple = (x, y, weight)
    return d.cons(triple, acc_list)

out_fold_prim = P.fold("out_fold", out_fold_leaf, acc=LIST(WEDGE), index=True)

# Main program
def prog(d, c_list, es_list):
    # Build clustering trie
    L_trie = d.call(lg, x=262143)
    c_init = d.call(const_zero, L=L_trie)
    c_trie = d.call(c_stream, list=c_list, init=(0, c_init))

    # Process edges
    req_init = d.call(mc_empty, L=18)
    acc_init = d.call(const_zero, L=18)

    acc_final = d.call(e_stream, list=es_list, init=(acc_init, req_init))

    # We've lost the req_q, so we can't deliver properly
    d.erase(c_trie)

    # Build output list
    output_list = d.call(out_fold_prim, t=acc_final, L=18, acc=d.nil())

    return output_list

P.prog("t5_rewrite_weighted", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("Wrote net.hvm")
