"""Strong-human-route comparators: Bend tree reductions over the SAME rope input, for 5 folds.
The author (me) writes them as a strong Bend author would: plain recursive `match`, both sub-reductions are independent
calls so they run in parallel, tuple state returned as Bend tuples, no list. Compiled with genome.bend_io.BEND_OPTS
(all optimisations, type checker off) and verified with genome.verify.verify_b1 on the rope-input programs.
Rope constructors in Bend (from bend_io.bend_type_decls): C0 = Nil, C1{f0} = One(x), C2{f0, f1} = Cat(l, r)."""

BEND = {}

BEND["sum"] = """
def prog(t):
  return red(t)

def red(t):
  match t:
    case Grope/C0:
      return 0
    case Grope/C1:
      return t.f0
    case Grope/C2:
      return red(t.f0) + red(t.f1)
"""

BEND["max"] = """
def prog(t):
  return red(t)

def red(t):
  match t:
    case Grope/C0:
      return 0
    case Grope/C1:
      return t.f0
    case Grope/C2:
      a = red(t.f0)
      b = red(t.f1)
      if a > b:
        return a
      else:
        return b
"""

BEND["argmax_first"] = """
def prog(t):
  (b, i, n) = red(t)
  return i

def red(t):
  match t:
    case Grope/C0:
      return (0, 0, 0)
    case Grope/C1:
      return (t.f0, 0, 1)
    case Grope/C2:
      (b1, i1, n1) = red(t.f0)
      (b2, i2, n2) = red(t.f1)
      if b2 > b1:
        return (b2, n1 + i2, n1 + n2)
      else:
        return (b1, i1, n1 + n2)
"""

BEND["category_counts"] = """
def prog(t):
  return red(t)

def red(t):
  match t:
    case Grope/C0:
      return (0, 0, 0, 0, 0, 0, 0)
    case Grope/C1:
      return (t.f0 == 0, t.f0 == 1, t.f0 == 2, t.f0 == 3, t.f0 == 4, t.f0 == 5, t.f0 == 6)
    case Grope/C2:
      (a0, a1, a2, a3, a4, a5, a6) = red(t.f0)
      (b0, b1, b2, b3, b4, b5, b6) = red(t.f1)
      return (a0 + b0, a1 + b1, a2 + b2, a3 + b3, a4 + b4, a5 + b5, a6 + b6)
"""

BEND["first_violation"] = """
def prog(t):
  (n, f) = red(t)
  return f

def red(t):
  match t:
    case Grope/C0:
      return (0, 16777215)
    case Grope/C1:
      if t.f0 != 0:
        return (1, 0)
      else:
        return (1, 16777215)
    case Grope/C2:
      (n1, f1) = red(t.f0)
      (n2, f2) = red(t.f1)
      if f1 != 16777215:
        return (n1 + n2, f1)
      else:
        if f2 != 16777215:
          return (n1 + n2, n1 + f2)
        else:
          return (n1 + n2, 16777215)
"""

FOLDS = list(BEND)
