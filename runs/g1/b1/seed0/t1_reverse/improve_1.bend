def prog(xs):
  return reverse_blocks(xs, [])

def reverse_blocks(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      a = xs.head
      ys = xs.tail
      match ys:
        case List/Nil:
          return List/Cons(a, acc)
        case List/Cons:
          b = ys.head
          zs = ys.tail
          match zs:
            case List/Nil:
              return List/Cons(b, List/Cons(a, acc))
            case List/Cons:
              c = zs.head
              ws = zs.tail
              match ws:
                case List/Nil:
                  return List/Cons(c, List/Cons(b, List/Cons(a, acc)))
                case List/Cons:
                  d = ws.head
                  rest = ws.tail
                  return reverse_blocks(rest, List/Cons(d, List/Cons(c, List/Cons(b, List/Cons(a, acc)))))
