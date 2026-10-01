import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.graphprims import Book

D = os.path.dirname(os.path.abspath(__file__))
b = Book()
b.add("""
@st = (b (i (p (j o))))
  & b ~ {b1 b2}
  & p ~ {p1 p2}
  & b1 ~ $([<] $(p1 lt))
  & lt ~ ?((@st_no @st_yes) (b2 (i (p2 (j o)))))
@st_no = (b (i (* (* (b i)))))
@st_yes = (* (* (* (p (j (p j))))))
@fin_ok = (i i)
@fin_abs = (* (* 6))
""")
pat = "(* *)"
for k in range(5, -1, -1):
    pat = f"(* (p{k} {pat}))"
lines = [f"@prog = ((tau {pat}) out)"]
lines.append("  & @st ~ (p0 (0 (p1 (1 (b1 i1)))))")
for k in range(2, 6):
    lines.append(f"  & @st ~ (b{k-1} (i{k-1} (p{k} ({k} (b{k} i{k})))))")
lines.append("  & b5 ~ $([<] $(tau lt))")
lines.append("  & lt ~ ?((@fin_ok @fin_abs) (i5 out))")
b.add("\n".join(lines))
open(os.path.join(D, "net.hvm"), "w").write(b.text())
