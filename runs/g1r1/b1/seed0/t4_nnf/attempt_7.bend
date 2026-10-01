def prog(x):
  return norm(x, 0)

def norm(v, mode):
  match v:
    case Gbool/C0:
      if mode == 0:
        return Gbool/C0
      else:
        return Gbool/C1
    case Gbool/C1:
      if mode == 0:
        return Gbool/C1
      else:
        return Gbool/C0
    case Gbool/C2:
      if mode == 0:
        return Gbool/C2(v.f0)
      else:
        return Gbool/C3(Gbool/C2(v.f0))
    case Gbool/C3:
      if mode == 0:
        return norm(v.f0, 1)
      else:
        return norm(v.f0, 0)
    case Gbool/C4:
      if mode == 0:
        return Gbool/C4(norm(v.f0, 0), norm(v.f1, 0))
      else:
        return Gbool/C5(norm(v.f0, 1), norm(v.f1, 1))
    case Gbool/C5:
      if mode == 0:
        return Gbool/C5(norm(v.f0, 0), norm(v.f1, 0))
      else:
        return Gbool/C4(norm(v.f0, 1), norm(v.f1, 1))
