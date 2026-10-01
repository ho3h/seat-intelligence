import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "<home>/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

K = 16
STEP = """((L g) ((u v) (L3 g3)))
  & L ~ {L1 {L2 L3}}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & @gl_adj ~ (g (u1 (L1 ((v1 1) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 1) g3))))"""

b = Book()
G.lg(b); G.adjacency(b); G.sssp(b, "sp"); G.get(b, "gt")
G.stream(b, "w", K, STEP, "((* g) g)")
b.add("""
@prog = ((n (s (t es))) out)
  & n ~ ?(((* (* (* 16777215))) @p_pos) (s (t (es out))))
@p_pos = (nm1 (s (t (es out))))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @sp_sssp ~ (n (s (L3 (16777215 (G D)))))
  & @gt ~ (D (t (L4 out)))
""")
open(os.path.join(D, "net.hvm"), "w").write(b.text())
