def prog(x):
  return pos(x)

def pos(f):
  match f:
    case Gbool/C0:
      return Gbool/C0
    case Gbool/C1:
      return Gbool/C1
    case Gbool/C2:
      return f
    case Gbool/C3:
      return neg(f.f0)
    case Gbool/C4:
      return Gbool/C4(pos(f.f0), pos(f.f1))
    case Gbool/C5:
      return Gbool/C5(pos(f.f0), pos(f.f1))

def neg(f):
  match f:
    case Gbool/C0:
      return Gbool/C1
    case Gbool/C1:
      return Gbool/C0
    case Gbool/C2:
      return Gbool/C3(f.f0)
    case Gbool/C3:
      return pos(f.f0)
    case Gbool/C4:
      return Gbool/C5(neg(f.f0), neg(f.f1))
    case Gbool/C5:
      return Gbool/C4(neg(f.f0), neg(f.f1))
