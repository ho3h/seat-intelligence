def prog(x):
  return value_of(x)

def value_of(x):
  match x:
    case Gexpr/C0:
      return x.f0
    case Gexpr/C1:
      return value_of(x.f0) + value_of(x.f1)
    case Gexpr/C2:
      return value_of(x.f0) * value_of(x.f1)
