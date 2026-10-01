def prog(x):
  match x:
    case Gexpr/C0:
      return x.f0
    case Gexpr/C1:
      match x.f0:
        case Gexpr/C0:
          match x.f1:
            case Gexpr/C0:
              return x.f0.f0 + x.f1.f0
            case Gexpr/C1:
              return x.f0.f0 + prog(x.f1.f0) + prog(x.f1.f1)
            case Gexpr/C2:
              return x.f0.f0 + prog(x.f1.f0) * prog(x.f1.f1)
        case Gexpr/C1:
          match x.f1:
            case Gexpr/C0:
              return (prog(x.f0.f0) + prog(x.f0.f1)) + x.f1.f0
            case Gexpr/C1:
              return (prog(x.f0.f0) + prog(x.f0.f1)) + prog(x.f1.f0) + prog(x.f1.f1)
            case Gexpr/C2:
              return (prog(x.f0.f0) + prog(x.f0.f1)) + prog(x.f1.f0) * prog(x.f1.f1)
        case Gexpr/C2:
          match x.f1:
            case Gexpr/C0:
              return (prog(x.f0.f0) * prog(x.f0.f1)) + x.f1.f0
            case Gexpr/C1:
              return (prog(x.f0.f0) * prog(x.f0.f1)) + prog(x.f1.f0) + prog(x.f1.f1)
            case Gexpr/C2:
              return (prog(x.f0.f0) * prog(x.f0.f1)) + prog(x.f1.f0) * prog(x.f1.f1)
    case Gexpr/C2:
      match x.f0:
        case Gexpr/C0:
          match x.f1:
            case Gexpr/C0:
              return x.f0.f0 * x.f1.f0
            case Gexpr/C1:
              return x.f0.f0 * (prog(x.f1.f0) + prog(x.f1.f1))
            case Gexpr/C2:
              return x.f0.f0 * (prog(x.f1.f0) * prog(x.f1.f1))
        case Gexpr/C1:
          match x.f1:
            case Gexpr/C0:
              return (prog(x.f0.f0) + prog(x.f0.f1)) * x.f1.f0
            case Gexpr/C1:
              return (prog(x.f0.f0) + prog(x.f0.f1)) * (prog(x.f1.f0) + prog(x.f1.f1))
            case Gexpr/C2:
              return (prog(x.f0.f0) + prog(x.f0.f1)) * (prog(x.f1.f0) * prog(x.f1.f1))
        case Gexpr/C2:
          match x.f1:
            case Gexpr/C0:
              return (prog(x.f0.f0) * prog(x.f0.f1)) * x.f1.f0
            case Gexpr/C1:
              return (prog(x.f0.f0) * prog(x.f0.f1)) * (prog(x.f1.f0) + prog(x.f1.f1))
            case Gexpr/C2:
              return (prog(x.f0.f0) * prog(x.f0.f1)) * (prog(x.f1.f0) * prog(x.f1.f1))
