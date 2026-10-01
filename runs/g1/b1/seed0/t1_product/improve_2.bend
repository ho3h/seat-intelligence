def prog(xs):
  return product(xs, 1)

def product(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      a = acc * xs.head
      ys = xs.tail
      match ys:
        case List/Nil:
          return a
        case List/Cons:
          b = a * ys.head
          zs = ys.tail
          match zs:
            case List/Nil:
              return b
            case List/Cons:
              c = b * zs.head
              ws = zs.tail
              match ws:
                case List/Nil:
                  return c
                case List/Cons:
                  d = c * ws.head
                  if d == 0:
                    return 0
                  else:
                    return product(ws.tail, d)
