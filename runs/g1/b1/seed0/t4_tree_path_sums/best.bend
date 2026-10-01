def prog(x):
  return walk(x, 0, [])

def walk(t, acc, out):
  match t:
    case Gtree/C0:
      return out
    case Gtree/C1:
      s = acc + t.f1
      match t.f0:
        case Gtree/C0:
          match t.f2:
            case Gtree/C0:
              return List/Cons(s, out)
            case Gtree/C1:
              return walk(t.f2, s, out)
        case Gtree/C1:
          out1 = walk(t.f2, s, out)
          return walk(t.f0, s, out1)
