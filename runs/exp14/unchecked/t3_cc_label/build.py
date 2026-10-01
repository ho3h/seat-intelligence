"""Build net for t3_cc_label: output minimum vertex id in each connected component"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
# D = /Users/tedsandtads/Genome/runs/exp14/unchecked/t3_cc_label
# Need to add /Users/tedsandtads/Genome to path
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

K = 16  # walker lookahead for list processing

# Walker step for undirected edges: each edge (u,v) creates pushes on both u's and v's adjacency lists
UND_STEP = """((L g) ((u v) (L3 g3)))
  & L ~ {L1 {L2 L3}}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & @gl_adj ~ (g (u1 (L1 ((v1 0) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 0) g3))))"""


def build():
    b = Book()

    # Core primitives
    G.lg(b)                              # compute log(n-1) = trie depth
    G.relax(b, "cc")                     # min-label connected components frontier
    G.adjacency(b)                       # push edges into adjacency trie
    G.const_trie(b, "gl_inf", "16777215")  # infinity trie for initial distances
    G.iota_trie(b, "io")                 # trie with leaf i = base + i
    G.to_list(b, "tl")                   # convert trie to list (first n leaves)
    G.stream(b, "w", K, UND_STEP, "((* g) g)")  # stream through edges

    # Main program: handle n=0 case separately, then run frontier
    b.add("""
@prog = ((n es) out)
  & n ~ ?(((* (0 *)) @p_pos) (es out))
@p_pos = (nm1 (es out))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 {L4 {L5 L6}}}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @gl_inf ~ (L3 D0)
  & @io ~ (L4 (0 C0))
  & @cc_loop ~ ((G (D0 (C0 (L5 16777215)))) D)
  & @tl ~ (D (L6 (0 (n ((0 *) out)))))
""")

    return b


if __name__ == "__main__":
    b = build()
    path = os.path.join(D, "net.hvm")
    open(path, "w").write(b.text())
    print("wrote", path)
