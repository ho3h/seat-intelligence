import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book
D = os.path.dirname(os.path.abspath(__file__))
K = 16
UND_STEP = """((L g) ((u v) (L3 g3)))
  & L ~ {L1 {L2 L3}}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & @gl_adj ~ (g (u1 (L1 ((v1 0) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 0) g3))))"""
b = Book(); G.lg(b); G.relax(b, "cc"); G.adjacency(b); G.const_trie(b, "gl_inf", "16777215")
G.iota_trie(b, "io"); G.to_list(b, "tl"); G.stream(b, "w", K, UND_STEP, "((* g) g)")
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
open(os.path.join(D, "net.hvm"), "w").write(b.text())
