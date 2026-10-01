def prog(x):
  return positive(x)

def positive(f):
  match f:
    case Gbool/C0:
      return Gbool/C0
    case Gbool/C1:
      return Gbool/C1
    case Gbool/C2:
      return Gbool/C2(f.f0)
    case Gbool/C3:
      return negative(f.f0)
    case Gbool/C4:
      return Gbool/C4(positive(f.f0), positive(f.f1))
    case Gbool/C5:
      return Gbool/C5(positive(f.f0), positive(f.f1))

def negative(f):
  match f:
    case Gbool/C0:
      return Gbool/C1
    case Gbool/C1:
      return Gbool/C0
    case Gbool/C2:
      return Gbool/C3(Gbool/C2(f.f0))
    case Gbool/C3:
      return positive(f.f0)
    case Gbool/C4:
      return Gbool/C5(negative(f.f0), negative(f.f1))
    case Gbool/C5:
      return Gbool/C4(negative(f.f0), negative(f.f1))
