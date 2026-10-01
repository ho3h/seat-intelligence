"""The runtime aborts when a DUP meets a reference whose definition contains a DUP ("clone a non-affine global reference"). A statically
reduced copy of that definition has no DUP and does not abort. The normalizer models the abort and refuses to call such nets equal at every tier."""
from genome.executor import run_net
from genome.hero2.prove import Prover, TIERS
A = "@five = z\n  & 5 ~ {z w}\n  & w ~ *\n@prog = (x out)\n  & @five ~ {a b}\n  & a ~ $([+] $(b c))\n  & x ~ *\n  & c ~ out\n"
B = "@five = 5\n@prog = (x out)\n  & @five ~ {a b}\n  & a ~ $([+] $(b c))\n  & x ~ *\n  & c ~ out\n"
for name, book in (("A (five contains a DUP)", A), ("B (five statically reduced)", B)):
    r = run_net("@main = r\n  & @prog ~ (0 r)\n\n" + book, "run", 10)
    print(f"executor {name}: ok={r.ok} result={r.result!r} error={r.error[:70]!r}")
p = Prover(A, B)
for t in TIERS:
    v = p.compare(t)
    print(f"tier {t[0]:4s}: equal={v.equal} {v.reason}")
