import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

D = os.path.dirname(os.path.abspath(__file__))
b = Book()
G.lg(b); G.sssp(b, "rc"); G.adjacency(b)
G.reduce(b, "cnt", """(x (i (n o)))
  & i ~ $([<] $(n a))
  & x ~ $([!] $(16777215 c))
  & a ~ $([&] $(c o))""", "+", idx=True, env=True)
G.stream(b, "w", 16, """((L g) ((u v) (L3 g3)))
  & L ~ {L1 L3}
  & @gl_adj ~ (g (u (L1 ((v 1) g3))))""", "((* g) g)")
b.add("""
@prog = ((n (s es)) out)
  & n ~ ?(((* (* 1)) @p_pos) (s (es out)))
@p_pos = (nm1 (s (es out)))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & n ~ {n1 n2}
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @rc_sssp ~ (n1 (s (L3 (16777215 (G Dt)))))
  & @cnt ~ (Dt (L4 (0 (n2 out))))
""")
open(os.path.join(D, "net.hvm"), "w").write(b.text())
