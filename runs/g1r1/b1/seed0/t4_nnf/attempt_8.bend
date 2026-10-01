def prog(x):
  return positive(x)

def positive(v):
  match v:
    case Gbool/C0:
      return Gbool/C0
    case Gbool/C1:
      return Gbool/C1
    case Gbool/C2:
      return Gbool/C2(v.f0)
    case Gbool/C3:
      return negative(v.f0)
    case Gbool/C4:
      return Gbool/C4(positive(v.f0), positive(v.f1))
    case Gbool/C5:
      return Gbool/C5(positive(v.f0), positive(v.f1))

def negative(v):
  match v:
    case Gbool/C0:
      return Gbool/C1
    case Gbool/C1:
      return Gbool/C0
    case Gbool/C2:
      return Gbool/C3(Gbool/C2(v.f0))
    case Gbool/C3:
      return positive(v.f0)
    case Gbool/C4:
      return Gbool/C5(negative(v.f0), negative(v.f1))
    case Gbool/C5:
      return Gbool/C4(negative(v.f0), negative(v.f1))
