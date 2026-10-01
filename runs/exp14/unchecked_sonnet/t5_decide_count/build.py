import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

D = os.path.dirname(os.path.abspath(__file__))
b = Book()
# walker state (tau acc); element (u (v s)); count s >= tau
G.stream(b, "w", 16, """((tau acc) ((* (* s)) (tau2 acc2)))
  & tau ~ {t1 tau2}
  & s ~ $([<] $(t1 lt))
  & 1 ~ $([-] $(lt g))
  & acc ~ $([+] $(g acc2))""", "((* acc) acc)")
b.add("""
@prog = ((tau es) out)
  & @w_blk ~ (es ((tau 0) out))
""")
open(os.path.join(D, "net.hvm"), "w").write(b.text())
