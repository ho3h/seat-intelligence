def prog(x):
  return walk(x, 0)

def walk(t, acc):
  match t:
    case Gtree/C0:
      return []
    case Gtree/C1:
      s = acc + t.f1
      match t.f0:
        case Gtree/C0:
          match t.f2:
            case Gtree/C0:
              return [s]
            case Gtree/C1:
              return walk(t.f2, s)
        case Gtree/C1:
          match t.f2:
            case Gtree/C0:
              return walk(t.f0, s)
            case Gtree/C1:
              return append(walk(t.f0, s), walk(t.f2, s))

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))
