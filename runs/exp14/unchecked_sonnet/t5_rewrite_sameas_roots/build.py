import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

D = os.path.dirname(os.path.abspath(__file__))
K = 16
b = Book()
G.lg(b); G.const_trie(b, "z0", "0"); G.update(b, "dset", "set")
G.mc_empty(b, "rq0"); G.mc_request(b, "rq"); G.mc_deliver(b, "dl")
# walk 1: count and reverse the list
G.stream(b, "w1", K, "((c acc) (x (c2 (1 (x acc)))))\n  & c ~ $([+1] c2)", "((c acc) (c acc))")
# walk 2: reversed list -> trie, leaf i = p[i]
G.stream(b, "w2", K, """((L (i h)) (x (L3 (i2 h2))))
  & L ~ {L1 L3}
  & i ~ {i1 ip}
  & ip ~ $([-] $(1 i2))
  & @dset ~ (h (i1 (L1 (x h2))))""", "((* (* h)) h)")
# one pointer-jumping round: fold registers requests for key D[i], builds V (copy of D) and H (reply wires)
G.fold(b, "fl", """(x (i (E ((q (h v)) (q2 (h2 v2))))))
  & x ~ {x1 x2}
  & i ~ {i1 i2}
  & E ~ {E1 {E2 E3}}
  & @rq ~ (q (x1 (E1 (r q2))))
  & @dset ~ (v (i1 (E2 (x2 v2))))
  & @dset ~ (h (i2 (E3 (r h2))))""")
G.to_list(b, "tl")
b.add("""
@round = (D (L o))
  & L ~ {La {Lb {Lc {Ld {Le Lf}}}}}
  & @rq0 ~ (La Q0)
  & @z0 ~ (Lb H0)
  & @z0 ~ (Lc V0)
  & @fl ~ (D (Ld (0 (Le ((Q0 (H0 V0)) (Q (H V)))))))
  & @dl ~ (V (Q Lf))
  & H ~ o
@rounds = (D (c (L o)))
  & c ~ ?((@rd_z @rd_s) (D (L o)))
@rd_z = (D (* D))
@rd_s = (cm (D (L o)))
  & L ~ {L1 L2}
  & @round ~ (D (L1 D2))
  & @rounds ~ (D2 (cm (L2 o)))
@prog = (l out)
  & @w1_blk ~ (l ((0 (0 *)) (n rev)))
  & n ~ ?((@p_zero @p_pos) (rev out))
@p_zero = (* (0 *))
@p_pos = (nm1 (rev out))
  & nm1 ~ {a {c i0}}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 {L4 L5}}}}
  & @z0 ~ (L1 H0)
  & @w2_blk ~ (rev ((L2 (i0 H0)) H))
  & @rounds ~ (H (L3 (L4 Dr)))
  & @tl ~ (Dr (L5 (0 (n ((0 *) out)))))
""")
open(os.path.join(D, "net.hvm"), "w").write(b.text())
print("ok", b.size())
