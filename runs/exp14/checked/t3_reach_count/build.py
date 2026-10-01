"""Build script for t3_reach_count: count vertices reachable from source s in a directed graph."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
# Go up 4 levels: checked/t3_reach_count -> checked -> exp14 -> runs -> Genome
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib.glue import Program, NUM, DEPTH, TRIE, ADJ, EDGE, LIST, INF


def build():
    P = Program()

    # Primitives
    lg = P.lg()                                  # compute depth from n-1
    empty_adj = P.empty_adj()                   # empty adjacency trie
    adj = P.adjacency()                         # add edge to adjacency
    sssp = P.sssp("sp")                         # single-source shortest path (reachability)

    # Walker for building adjacency trie from edge list
    def step(d, L, g, u, v):
        # For directed graph: add edge u -> v
        L1, L2 = d.fanout(L, 2)
        g2 = d.call(adj, G=g, u=u, L=L1, v=v, w=0)
        return L2, g2

    def fin(d, L, g):
        d.erase(L)
        return g

    w = P.stream("w", step, fin, state=[("L", DEPTH), ("g", ADJ)], elem=EDGE)

    # Count reachable vertices: count how many have distance < INF (and index < n for padding)
    def count_reach(d, dist, i, n):
        # Check if distance is finite (< INF means reachable)
        is_reach = d.op(dist, "<", INF)
        # Check if index is valid (< n, so not padding)
        i_valid = d.op(i, "<", n)
        # Count both conditions met
        both = d.op(is_reach, "&", i_valid)
        return both

    cnt = P.reduce("cnt", count_reach, "+", index=True, env=NUM)

    def prog(d, n, s, es):
        def empty(b, s, es):
            # n = 0: no vertices, source can't exist
            b.erase(s)
            b.erase(es)
            return 1

        def nonempty(b, nm1, s, es):
            # n >= 1: compute reach_count
            nm1a, nm1b = b.fanout(nm1, 2)
            n = b.op(nm1b, "+", 1)
            n1, n2 = b.fanout(n, 2)

            # Compute depth L = lg(n-1)
            L = b.call(lg, x=nm1a)
            L1, L2, L3, L4 = b.fanout(L, 4)

            # Build adjacency trie from edges
            G = b.call(w, list=es, init=(L2, b.call(empty_adj, L=L1)))

            # Compute reachable set using SSSP (all edges have weight 0)
            # Distance[v] = 0 if v = s or reachable from s, INF otherwise
            D = b.call(sssp, n=n1, s=s, L=L3, G=G)

            # Count vertices with distance < INF
            result = b.call(cnt, t=D, L=L4, E=n2)
            return result

        return d.branch(n, empty, nonempty, s, es)

    P.prog("t3_reach_count", prog)
    P.write(os.path.join(D, "net.hvm"))
    print(f"Built net.hvm in {D}")


if __name__ == "__main__":
    build()
