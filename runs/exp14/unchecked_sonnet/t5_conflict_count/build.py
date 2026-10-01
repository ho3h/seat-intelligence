import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

D = os.path.dirname(os.path.abspath(__file__))
K = 16
b = Book()
G.lg(b)
G.const_trie(b, "z0", "0")
G.update(b, "cs", "set")
G.update(b, "rq", "reply")
G.mc_empty(b, "qe")
G.mc_deliver(b, "dl")
# pass 1: count cells and build the reversed list
G.stream(b, "w1", K, """((cnt acc) (e (cnt2 (1 (e acc)))))
  & cnt ~ $([+1] cnt2)""", "((cnt acc) (cnt acc))")
# pass 2: walk reversed list from idx n-1 down, set trie[idx] = c
G.stream(b, "w2", K, """((L (idx T)) (e (L3 (idx2 T2))))
  & L ~ {L1 L3}
  & idx ~ {i1 i2}
  & i2 ~ $([-] $(1 idx2))
  & @cs ~ (T (i1 (L1 (e T2))))""", "((* (* T)) T)")
# pass 3: walk must-not-link pairs, register lookups of c[u], c[v]
G.stream(b, "w3", K, """((L (q cnt)) ((u v) (L3 (q2 cnt2))))
  & L ~ {L1 {L2 L3}}
  & @rq ~ (q (u (L1 (ra q1))))
  & @rq ~ (q1 (v (L2 (rb q2))))
  & ra ~ $([=] $(rb eq))
  & cnt ~ $([+] $(eq cnt2))""", "((* (q cnt)) (q cnt))")
b.add("""
@prog = ((c mnl) out)
  & @w1_blk ~ (c ((0 (0 *)) (n R)))
  & n ~ ?((@p_zero @p_pos) (R (mnl out)))
@p_zero = (* (* 0))
@p_pos = (nm1 (R (mnl out)))
  & nm1 ~ {a c}
  & @lg ~ (a L)
  & L ~ {L1 {L2 {L3 {L4 L5}}}}
  & @z0 ~ (L1 C0)
  & @w2_blk ~ (R ((L2 (c C0)) C))
  & @qe ~ (L3 Q0)
  & @w3_blk ~ (mnl ((L4 (Q0 0)) (Q out)))
  & @dl ~ (C (Q L5))
""")
open(os.path.join(D, "net.hvm"), "w").write(b.text())
