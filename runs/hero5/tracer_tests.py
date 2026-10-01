"""Unit tests of the tracer's provenance semantics on hand-written nets (facts are the defs named fact_k).
usage: python3 runs/hero5/tracer_tests.py   (asserts; prints PASS)"""
import sys, os, subprocess, re
sys.path.insert(0, '/Users/tedsandtads/Genome')
from genome.hero5.core import TRACER, _tmp
from genome.executor import ENV

def run(book, mode, F=8):
    path = _tmp(book)
    try:
        p = subprocess.run([TRACER, "run", path], capture_output=True, text=True, env=dict(ENV, GENOME_TR=str(mode), GENOME_TR_F=str(F)))
    finally:
        os.unlink(path)
    out = p.stdout
    toks = re.search(r"^TOKENS (.*)$", out, re.M).group(1).split()
    sets = {int(m.group(1)): [int(x) for x in m.group(2).split(",") if x] for m in re.finditer(r"^SET (\d+) ?(.*)$", out, re.M)}
    return [(t.rsplit(":", 1)[0], sets[int(t.rsplit(":", 1)[1])]) for t in toks]

A = """@main = r
  & @f ~ (@fact_0 (@fact_1 (@fact_2 (@fact_3 r))))
@fact_0 = 5
@fact_1 = 7
@fact_2 = 9
@fact_3 = 11
@f = (a (b (c (d out))))
  & a ~ $([+] $(b s))
  & c ~ {c1 c2}
  & d ~ *
  & out ~ (s (c1 c2))
"""
B = """@main = r
  & @g ~ (@fact_0 r)
@fact_0 = 1
@g = (n out)
  & n ~ ?((@z @s) out)
@z = out
  & out ~ 7
@s = (nm1 out)
  & nm1 ~ *
  & out ~ 42
"""
for mode in (1, 2):
    r = run(A, mode)
    assert r[1] == ("N12", [0, 1]), r          # OPR: union of the two operands; nothing from the erased/copied facts
    assert r[3][1] == [2] and r[4][1] == [2], r  # DUP copies keep provenance
    assert all(3 not in s for _, s in r), r    # ERA drops provenance (fact 3)
assert run(B, 1)[0] == ("N42", []), run(B, 1)   # data policy: the branch choice is invisible
assert run(B, 2)[0] == ("N42", [0]), run(B, 2)  # full policy: switch value taints the chosen branch

# C: positive control. Keyed lookup in a 4-leaf tree whose leaves are facts: only the looked-up leaf is in the answer.
C = """@main = r
  & @get ~ (((@fact_0 @fact_1) (@fact_2 @fact_3)) (KEY r))
@fact_0 = 10
@fact_1 = 20
@fact_2 = 30
@fact_3 = 40
@get = (tree (k out))
  & k ~ {k1 k2}
  & k1 ~ $([/] $(2 hi))
  & k2 ~ $([%] $(2 lo))
  & hi ~ ?((@p0 @p1) (tree (lo out)))
@p0 = ((left right) (lo out))
  & right ~ *
  & lo ~ ?((@s0 @s1) (left out))
@p1 = (z ((left right) (lo out)))
  & z ~ *
  & left ~ *
  & lo ~ ?((@s0 @s1) (right out))
@s0 = ((x y) out)
  & y ~ *
  & x ~ out
@s1 = (z ((x y) out))
  & z ~ *
  & x ~ *
  & y ~ out
"""
for key in range(4):
    for mode in (1, 2):
        r = run(C.replace("KEY", str(key)), mode)
        assert r[0][1] == [key], (key, mode, r)      # exactly the fact that was read, under both policies
# D: over-attribution control. max of four facts by comparisons: the answer is one fact, the comparisons touch all of them.
D = """@main = r
  & @mx ~ (@fact_0 (@fact_1 (@fact_2 (@fact_3 r))))
@fact_0 = 10
@fact_1 = 40
@fact_2 = 30
@fact_3 = 20
@mx = (a (b (c (d out))))
  & @max2 ~ (a (b m1))
  & @max2 ~ (c (d m2))
  & @max2 ~ (m1 (m2 out))
@max2 = (x (y out))
  & x ~ {x1 x2}
  & y ~ {y1 y2}
  & x1 ~ $([>] $(y1 g))
  & g ~ ?((@keepy @keepx) (x2 (y2 out)))
@keepy = (x (y out))
  & x ~ *
  & y ~ out
@keepx = (z (x (y out)))
  & z ~ *
  & y ~ *
  & x ~ out
"""
r2 = run(D, 2); r1 = run(D, 1)
print("max-of-four provenance: data policy", r1, " full policy", r2)
assert r1[0] == ("Rfact_1", [1])                          # D: where-provenance names only the fact the answer was copied from
assert r2[0][0] == "Rfact_1" and sorted(r2[0][1]) == [0, 1, 2, 3]   # F: every compared fact (over-attribution by design)
print("PASS tracer semantics")
