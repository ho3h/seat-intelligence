def prog(x):
  return nnf(x, 0)

def nnf(f, negated):
  match f:
    case Gbool/C0:
      if negated == 0:
        return Gbool/C0
      else:
        return Gbool/C1
    case Gbool/C1:
      if negated == 0:
        return Gbool/C1
      else:
        return Gbool/C0
    case Gbool/C2:
      if negated == 0:
        return Gbool/C2(f.f0)
      else:
        return Gbool/C3(Gbool/C2(f.f0))
    case Gbool/C3:
      if negated == 0:
        return nnf(f.f0, 1)
      else:
        return nnf(f.f0, 0)
    case Gbool/C4:
      if negated == 0:
        return Gbool/C4(nnf(f.f0, 0), nnf(f.f1, 0))
      else:
        return Gbool/C5(nnf(f.f0, 1), nnf(f.f1, 1))
    case Gbool/C5:
      if negated == 0:
        return Gbool/C5(nnf(f.f0, 0), nnf(f.f1, 0))
      else:
        return Gbool/C4(nnf(f.f0, 1), nnf(f.f1, 1))
