def prog(x):
  match x:
    case Gexpr/C0:
      return x.f0
    case Gexpr/C1:
      return prog(x.f0) + prog(x.f1)
    case Gexpr/C2:
      return prog(x.f0) * prog(x.f1)
