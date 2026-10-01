def prog(xs):
  return map_inc(xs)

def map_inc(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      x1 = xs.head
      ys = xs.tail
      match ys:
        case List/Nil:
          return List/Cons(x1 + 1, List/Nil)
        case List/Cons:
          x2 = ys.head
          zs = ys.tail
          match zs:
            case List/Nil:
              return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Nil))
            case List/Cons:
              x3 = zs.head
              ws = zs.tail
              match ws:
                case List/Nil:
                  return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Nil)))
                case List/Cons:
                  x4 = ws.head
                  return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, map_inc(ws.tail)))))
