def prog(x):
  return deriv(x)

def deriv(e):
  match e:
    case Gvexpr/C0:
      return Gvexpr/C0(0)
    case Gvexpr/C1:
      d0 = deriv(e.f0)
      d1 = deriv(e.f1)
      return Gvexpr/C1(d0, d1)
    case Gvexpr/C2:
      d0 = deriv(e.f0)
      d1 = deriv(e.f1)
      return Gvexpr/C1(Gvexpr/C2(d0, e.f1), Gvexpr/C2(e.f0, d1))
    case Gvexpr/C3:
      if e.f0 == 0:
        return Gvexpr/C0(1)
      else:
        return Gvexpr/C0(0)
