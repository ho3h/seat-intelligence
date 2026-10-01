"""
HVM2 net for t5_rewrite_sameas_cycle: cycle detection in a pointer list.

Algorithm:
1. Use stream to walk the list
2. For each element (pointer value at index i), add edge i <- pointer_value
3. Mark nodes as roots where pointer_value == i (value 1 if root, 0 otherwise)
4. Run max-label relaxation to propagate "reachable from root"
5. After convergence, check if any node is unreachable (value == 0)
6. Output 1 if any unreachable, else 0

We use L=24 (maximum depth for 24-bit numbers) as a constant.
"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))

from genome.lib.glue import Program, NUM, TRIE, ADJ

P = Program()

MAX_L = 24

# Primitives
empty_adj = P.empty_adj()
adj_add = P.adjacency()
set_val = P.update("set_state", "set")
const_zero = P.const_trie("z0", 0)
relax_max = P.relax("relax_max", maximize=True)
reduce_or = P.reduce("reduce_check", lambda d, x: x, "|", index=False, env=None)

# Stream to process list: build adjacency graph and initial reachability state
# State: (index, adjacency, d_state)
def step(d, index, g, d_state, ptr_val):
    ptr1, ptr2 = d.fanout(ptr_val, 2)
    idx1, idx2, idx3, idx4 = d.fanout(index, 4)

    # Add reverse edge: ptr_val -> index
    g2 = d.call(adj_add, G=g, u=ptr1, L=MAX_L, v=idx1, w=1)

    # Mark as root if ptr_val == index
    is_root = d.op(ptr2, "=", idx2)
    d2 = d.call(set_val, t=d_state, k=idx3, L=MAX_L, P=is_root)

    # Increment index
    index_next = d.op(idx4, "+", 1)

    return index_next, g2, d2

def fin(d, index, g, d_state):
    d.erase(index)

    # Create initial messages trie (all zeros)
    c_init = d.call(const_zero, L=MAX_L)

    # Run relaxation: max-label propagation from roots
    # D[i] = 1 if i is a root, 0 otherwise (from d_state)
    # C[i] = 0 initially (from c_init)
    # message[i] = d2[i] * 1 where d2[i] = max(d[i], c[i])
    # Convergence: d[i] = 1 if i can reach a root, else 0
    d_final = d.call(relax_max, G=g, D=d_state, C=c_init, L=MAX_L)

    # Check for cycles: if any node has value 0, it's unreachable (in a cycle)
    # reduce with OR: result = d_final[0] | d_final[1] | ... | d_final[n-1]
    # If result == 0, at least one node is unreachable (cycle exists)
    result = d.call(reduce_or, t=d_final, L=MAX_L)

    # has_cycle = 1 if result == 0, else 0
    has_cycle = d.op(result, "=", 0)

    return has_cycle

stream_process = P.stream("process_stream", step, fin,
                          state=[("index", NUM), ("g", ADJ), ("d_state", TRIE(NUM))],
                          elem=NUM)

def prog(d, p):
    # Initialize structures
    empty_g = d.call(empty_adj, L=MAX_L)
    d_init = d.call(const_zero, L=MAX_L)

    # Process list (includes relaxation and cycle check in fin)
    has_cycle = d.call(stream_process, list=p, init=(0, empty_g, d_init))

    return has_cycle

P.prog("t5_rewrite_sameas_cycle", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
print("wrote net.hvm")
