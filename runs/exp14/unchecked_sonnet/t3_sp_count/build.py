import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

D = os.path.dirname(os.path.abspath(__file__))
b = Book()
G.lg(b)
G.adjacency(b)
G.const_trie(b, "z00", "(0 0)")
G.update(b, "cs", "set")
G.get(b, "gt")

# state leaf (vis cnt); message/combined leaf (nmsg sum)
ACT = """(X ((vis cnt) ((nm sum) (d2 (f m)))))
  & X ~ *
  & nm ~ $([>] $(0 pos))
  & vis ~ {vis1 vis2}
  & vis1 ~ $([=] $(0 nv))
  & pos ~ $([&] $(nv go))
  & go ~ ?((@cnt_no @cnt_yes) (vis2 (cnt (sum (d2 (f m))))))
@cnt_no = (vis (cnt (sum ((vis cnt) (0 0)))))
  & sum ~ *
@cnt_yes = (* (vis (cnt (sum ((1 s1) (1 s2))))))
  & vis ~ *
  & cnt ~ *
  & sum ~ {s1 s2}"""
MSG = "(m (w (1 m)))\n  & w ~ *"
COMB = """((n s) ((cn cs) (n2 s2)))
  & n ~ $([+] $(cn n2))
  & s ~ $([+] $(cs s2))"""
G.frontier(b, "cnt", ACT, MSG, COMB, "(0 0)")

G.stream(b, "w", 16, """((L g) ((u v) (L3 g3)))
  & L ~ {L1 L3}
  & @gl_adj ~ (g (u (L1 ((v 0) g3))))""", "((* g) g)")

b.add("""
@prog = ((n (s (t es))) out)
  & n ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 {L4 {L5 {L6 L7}}}}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @z00 ~ (L3 D0)
  & @z00 ~ (L4 Ci)
  & @cs ~ (Ci (s (L5 ((1 1) C0))))
  & @cnt_loop ~ ((G (D0 (C0 (L6 0)))) Df)
  & @gt ~ (Df (t (L7 (* out))))
""")
open(os.path.join(D, "net.hvm"), "w").write(b.text())
