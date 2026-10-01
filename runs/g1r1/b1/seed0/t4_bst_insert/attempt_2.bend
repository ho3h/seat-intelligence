def prog(input):
  (x, t) = input
  return insert(x, t)

def insert(x, t):
  match t:
    case Gtree/C0:
      return Gtree/C1(Gtree/C0, x, Gtree/C0)
    case Gtree/C1:
      if x < t.f1:
        return Gtree/C1(insert(x, t.f0), t.f1, t.f2)
      else:
        if x > t.f1:
          return Gtree/C1(t.f0, t.f1, insert(x, t.f2))
        else:
          return t
