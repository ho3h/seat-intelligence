import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.graphprims import Book
D = os.path.dirname(os.path.abspath(__file__))
b = Book()
b.add("""
@prog = ((tau cs) out)
  & @f ~ (cs (tau out))

@f = ((?((@f_nil @f_cons) (pl (tau out))) pl) (tau out))

@f_nil = (* (* (0 *)))

@f_cons = (* ((h t) (tau out)))
  & h ~ (u (v s))
  & s ~ {s1 s2}
  & tau ~ {t1 t2}
  & s1 ~ $([<] $(t1 lt))
  & lt ~ ?((@f_keep @f_drop) (u (v (s2 (t2 (t out))))))

@f_keep = (u (v (s (tau (t out)))))
  & out ~ (1 ((u (v s)) tout))
  & @f ~ (t (tau tout))

@f_drop = (* (u (v (s (tau (t out))))))
  & u ~ *
  & v ~ *
  & s ~ *
  & @f ~ (t (tau out))
""")
open(os.path.join(D, "net.hvm"), "w").write(b.text())
