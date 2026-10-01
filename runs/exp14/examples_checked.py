"""Worked examples for the CHECKED API (genome/lib/glue.py): t3_degrees and t3_cc_largest, re-expressed from the
strong author's raw compositions in runs/exp8/build.py.
usage: python3 runs/exp14/examples_checked.py  -> runs/exp14/typed_t3_degrees.hvm, runs/exp14/typed_t3_cc_largest.hvm"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(D)))
from genome.lib.glue import Program, NUM, DEPTH, TRIE, ADJ, EDGE, INF


def t3_degrees():
    # Input (n, edges), undirected. Output: list of n degrees.
    P = Program()
    lg = P.lg()
    zeros = P.const_trie("z0", 0)                 # trie of zeros
    inc = P.update("dinc", "inc")                 # leaf k += 1 (no payload port)
    tl = P.to_list("tl")

    def step(d, L, h, u, v):                      # walker state (L, h); list element (u, v)
        L1, L2, L3 = d.fanout(L, 3)               # L is needed 3 times
        h1 = d.call(inc, t=h, k=u, L=L1)
        h2 = d.call(inc, t=h1, k=v, L=L2)
        return L3, h2                             # the new state (L, h)

    def fin(d, L, h):
        d.erase(L)                                # L is not needed at the end
        return h
    w = P.stream("w", step, fin, state=[("L", DEPTH), ("h", TRIE(NUM))], elem=EDGE)

    def prog(d, n, es):
        def empty(b, es):                         # n == 0: output []
            b.erase(es)
            return b.nil()

        def nonempty(b, nm1, es):                 # nm1 = n - 1
            nm1a, nm1b = b.fanout(nm1, 2)
            L = b.call(lg, x=nm1a)
            L1, L2, L3 = b.fanout(L, 3)
            H = b.call(w, list=es, init=(L2, b.call(zeros, L=L1)))
            n = b.op(nm1b, "+", 1)
            return b.call(tl, t=H, L=L3, n=n)
        return d.branch(n, empty, nonempty, es)
    P.prog("t3_degrees", prog)
    return P


def t3_cc_largest():
    # Input (n, edges), undirected. Output: size of the largest connected component (0 for n = 0).
    # min-label relax -> scatter histogram (add 1 at key label[i]) -> reduce max
    P = Program()
    lg = P.lg()
    cc = P.relax("cc")                             # min-label propagation
    adj = P.adjacency()
    empty_adj = P.empty_adj()
    infs = P.const_trie("gl_inf", INF)
    iota = P.iota_trie("io")                       # leaf i = i
    zeros = P.const_trie("z0", 0)
    hadd = P.update("hadd", "add")

    def key(d, x, i, n):                           # leaf x = label of vertex i; count it if i < n
        return x, d.op(i, "<", n)                  # (key, payload)
    sc = P.scatter("sc", hadd, key)
    mx = P.reduce("mx", lambda d, x: x, "max")

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
            return 0

        def nonempty(b, nm1, es):
            nm1a, nm1b = b.fanout(nm1, 2)
            n = b.op(nm1b, "+", 1)
            L = b.call(lg, x=nm1a)
            L1, L2, L3, L4, L5, L6, L7, L8, L9 = b.fanout(L, 9)
            G = b.call(w, list=es, init=(L2, b.call(empty_adj, L=L1)))
            D = b.call(cc, G=G, D=b.call(infs, L=L3), C=b.call(iota, L=L4), L=L5)
            H = b.call(sc, t=D, L=L7, Lh=L8, E=n, H=b.call(zeros, L=L6))
            return b.call(mx, t=H, L=L9)
        return d.branch(n, empty, nonempty, es)
    P.prog("t3_cc_largest", prog)
    return P


if __name__ == "__main__":
    for f in (t3_degrees, t3_cc_largest):
        path = os.path.join(D, "typed_" + f.__name__ + ".hvm")
        f().write(path, f"{f.__name__}: composed through genome/lib/glue.py (checked API)")
        print("wrote", path)
