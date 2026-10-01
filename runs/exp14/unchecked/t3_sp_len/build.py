"""Build net for t3_sp_len: shortest path length in undirected unweighted graph.
Input: (n, s, t, edges)
Output: shortest path length from s to t (or 16777215 if unreachable or out of range, or 0 if s == t)
"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
# Go up: t3_sp_len -> unchecked -> exp14 -> runs -> Genome
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib import graphprims as G
from genome.lib.graphprims import Book, INF

K = 16  # walker lookahead

# For undirected edges, push both (u, v) and (v, u) with weight 1
UND_STEP = """((L g) ((u v) (L3 g3)))
  & L ~ {L1 {L2 L3}}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & @gl_adj ~ (g (u1 (L1 ((v1 1) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 1) g3))))"""

def t3_sp_len():
    b = Book()

    # Add primitives
    G.lg(b)                           # compute trie depth L = lg(n-1)
    G.const_trie(b, "z0", "(0 *)")   # empty adjacency trie
    G.adjacency(b)                     # push edges: @gl_adj
    G.sssp(b, "sp")                    # shortest paths
    G.get(b, "rd")                     # read single distance
    G.stream(b, "w", K, UND_STEP, "((* g) g)")  # walk undirected edges

    b.add("""
@prog = ((n (s (t es))) out)
  & n ~ ?((@n_zero @p_main) (s (t (es out))))

@n_zero = (s (t (es out)))
  & s ~ *
  & t ~ *
  & es ~ *
  & out ~ 16777215

@p_main = (nm1 (s (t (es out))))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @z0 ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @sp_sssp ~ (n (s (L3 (16777215 (G D)))))
  & @rd ~ (D (t (L4 out)))
""")

    return b

if __name__ == "__main__":
    b = t3_sp_len()
    path = os.path.join(D, "net.hvm")
    open(path, "w").write(b.text())
    print(f"wrote {path}")
