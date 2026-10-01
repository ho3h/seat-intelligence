def prog(x):
  return pos(x)

def pos(v):
  match v:
    case Gbool/C0:
      return Gbool/C0
    case Gbool/C1:
      return Gbool/C1
    case Gbool/C2:
      return Gbool/C2(v.f0)
    case Gbool/C3:
      return neg(v.f0)
    case Gbool/C4:
      return Gbool/C4(pos(v.f0), pos(v.f1))
    case Gbool/C5:
      return Gbool/C5(pos(v.f0), pos(v.f1))

def neg(v):
  match v:
    case Gbool/C0:
      return Gbool/C1
    case Gbool/C1:
      return Gbool/C0
    case Gbool/C2:
      return Gbool/C3(Gbool/C2(v.f0))
    case Gbool/C3:
      return pos(v.f0)
    case Gbool/C4:
      return Gbool/C5(neg(v.f0), neg(v.f1))
    case Gbool/C5:
      return Gbool/C4(neg(v.f0), neg(v.f1))
