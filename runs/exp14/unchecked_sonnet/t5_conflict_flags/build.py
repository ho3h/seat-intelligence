import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

D = os.path.dirname(os.path.abspath(__file__))
K = 16

b = Book()
G.lg(b)
G.const_trie(b, "cinf", "16777215")   # C0: padding leaves never equal their own index
G.const_trie(b, "z0", "0")            # flag trie
G.mc_empty(b, "qe")                   # empty request trie
G.update(b, "cset", "set")
G.update(b, "fu", "or")
G.mc_request(b, "rq")
G.mc_deliver_keep(b, "dk")
G.zip2(b, "zz", "(x (y (x y)))")

# walker over c: state (idx (L C)); element x = c[idx]
G.stream(b, "cw", K, """((idx (L C)) (x (idx3 (L3 C2))))
  & idx ~ {i1 i2}
  & i2 ~ $([+1] idx3)
  & L ~ {L1 L3}
  & @cset ~ (C (i1 (L1 (x C2))))""", "((n (* C)) (n C))")

# walker over mnl: state (L (q F)); element (a b)
G.stream(b, "mw", K, """((L (q F)) ((a b) (L4 (q3 F2))))
  & L ~ {L1 {L2 {L3 L4}}}
  & @rq ~ (q (a (L1 (ra q2))))
  & @rq ~ (q2 (b (L2 (rb q3))))
  & ra ~ {ra1 ra2}
  & ra1 ~ $([=] $(rb eq))
  & @fu ~ (F (ra2 (L3 (eq F2))))""", "((* (q F)) (q F))")

# output: fold over zipped (C copy, flags); keep leaf i when C[i] == i
b.add("""
@fl_no = (* (t t))
@fl_yes = (* (v (t (1 (v t)))))
@mkL_s = (nm1 o)
  & @lg ~ (nm1 o)
""")
G.fold(b, "fl", """((cc fl) (i (acc o)))
  & i ~ $([=] $(cc keep))
  & keep ~ ?((@fl_no @fl_yes) (fl (acc o)))""", idx=True, env=False)

b.add("""
@prog = ((c mnl) out)
  & @cw_blk ~ (c ((0 (L1 C0)) (n C)))
  & @cinf ~ (L2 C0)
  & n ~ ?((0 @mkL_s) L)
  & L ~ {L1 {L2 {L3 {L4 {L5 {L6 {L7 L8}}}}}}}
  & @z0 ~ (L3 F0)
  & @qe ~ (L4 Q0)
  & @mw_blk ~ (mnl ((L5 (Q0 F0)) (Q F)))
  & @dk ~ (C (Q (L6 Cc)))
  & @zz ~ (Cc (F (L7 Z)))
  & @fl ~ (Z (L8 (0 ((0 *) out))))
""")

open(os.path.join(D, "net.hvm"), "w").write(b.text())
print("wrote net.hvm")
