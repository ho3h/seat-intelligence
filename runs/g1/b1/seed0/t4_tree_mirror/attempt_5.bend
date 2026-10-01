def prog(x):
  return mirror(x)

def mirror(t):
  match t:
    case Gtree/C0:
      return Gtree/C0
    case Gtree/C1:
      return Gtree/C1(mirror(t.f2), t.f1, mirror(t.f0))
