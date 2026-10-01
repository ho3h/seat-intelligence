def prog(e):
  return deriv(e)

def deriv(e):
  match e:
    case Gvexpr/C0:
      return Gvexpr/C0(0)
    case Gvexpr/C1:
      return Gvexpr/C1(deriv(e.f0), deriv(e.f1))
    case Gvexpr/C2:
      return Gvexpr/C1(
        Gvexpr/C2(deriv(e.f0), e.f1),
        Gvexpr/C2(e.f0, deriv(e.f1))
      )
    case Gvexpr/C3:
      if e.f0 == 0:
        return Gvexpr/C0(1)
      else:
        return Gvexpr/C0(0)
