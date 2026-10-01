def prog(x):
  return deriv(x)

def deriv(e):
  match e:
    case vexpr/C0:
      return vexpr/C0(0)
    case vexpr/C1:
      return vexpr/C1(deriv(e.f0), deriv(e.f1))
    case vexpr/C2:
      return vexpr/C1(vexpr/C2(deriv(e.f0), e.f1), vexpr/C2(e.f0, deriv(e.f1)))
    case vexpr/C3:
      if e.f0 == 0:
        return vexpr/C0(1)
      else:
        return vexpr/C0(0)
