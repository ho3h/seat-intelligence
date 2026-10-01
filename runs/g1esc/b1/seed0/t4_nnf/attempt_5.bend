def prog(x):
  return pos(x)

def pos(f):
  match f:
    case C0:
      return C0
    case C1:
      return C1
    case C2:
      return f
    case C3:
      return neg(f.f0)
    case C4:
      return C4(pos(f.f0), pos(f.f1))
    case C5:
      return C5(pos(f.f0), pos(f.f1))

def neg(f):
  match f:
    case C0:
      return C1
    case C1:
      return C0
    case C2:
      return C3(f.f0)
    case C3:
      return pos(f.f0)
    case C4:
      return C5(neg(f.f0), neg(f.f1))
    case C5:
      return C4(neg(f.f0), neg(f.f1))
