def prog(x):
  return mirror(x)

def mirror(t):
  match t:
    case Gtree/C0:
      return Gtree/C0
    case Gtree/C1:
      left = mirror(t.f2)
      right = mirror(t.f0)
      return Gtree/C1(left, t.f1, right)
