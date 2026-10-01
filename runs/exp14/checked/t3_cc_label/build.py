#!/usr/bin/env python3
"""t3_cc_label: connected component labeling (min-label within each component).

Input: (n, edges) with n vertices 0..n-1 and a list of undirected edges.
Output: list of length n, where output[v] is the smallest vertex id in the component containing v.

Algorithm: min-label relax over the adjacency trie.
"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
GENOME_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D))))
sys.path.insert(0, GENOME_ROOT)
from genome.lib.glue import Program, NUM, DEPTH, TRIE, ADJ, EDGE, INF


def build():
    P = Program()
    lg = P.lg()
    cc = P.relax("cc")                          # min-label propagation
    adj = P.adjacency()
    empty_adj = P.empty_adj()
    iota = P.iota_trie("io")                    # leaf i = i (each vertex labeled with itself)
    infs = P.const_trie("gl_inf", INF)          # all infinite (unreachable)
    tl = P.to_list("tl")                        # extract as list

    # Walker: build adjacency trie from edges
    def step(d, L, g, u, v):
        L1, L2, L3 = d.fanout(L, 3)
        u1, u2 = d.fanout(u, 2)
        v1, v2 = d.fanout(v, 2)
        g2 = d.call(adj, G=g, u=u1, L=L1, v=v1, w=0)
        g3 = d.call(adj, G=g2, u=v2, L=L2, v=u2, w=0)
        return L3, g3

    def fin(d, L, g):
        d.erase(L)
        return g

    w = P.stream("w", step, fin, state=[("L", DEPTH), ("g", ADJ)], elem=EDGE)

    def prog(d, n, es):
        def empty(b, es):
            b.erase(es)
            return b.nil()

        def nonempty(b, nm1, es):
            nm1a, nm1b = b.fanout(nm1, 2)
            n = b.op(nm1b, "+", 1)
            L = b.call(lg, x=nm1a)
            L1, L2, L3, L4, L5, L6 = b.fanout(L, 6)

            # Build adjacency trie from edges
            G = b.call(w, list=es, init=(L2, b.call(empty_adj, L=L1)))

            # Run min-label relax
            # D initialized with infs (unreachable initially)
            # C seeded with iota (each vertex sends its own id)
            D = b.call(cc, G=G, D=b.call(infs, L=L3), C=b.call(iota, L=L4), L=L5)

            # Convert to list
            return b.call(tl, t=D, L=L6, n=n)

        return d.branch(n, empty, nonempty, es)

    P.prog("t3_cc_label", prog)
    P.write(os.path.join(D, "net.hvm"))
    print(f"wrote {os.path.join(D, 'net.hvm')}")


if __name__ == "__main__":
    build()
