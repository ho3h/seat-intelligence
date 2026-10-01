def prog(x):
  (xs, ys) = x
  return append4(xs, ys)

def append4(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      a = xs.head
      t = xs.tail
      match t:
        case List/Nil:
          return List/Cons(a, ys)
        case List/Cons:
          b = t.head
          u = t.tail
          match u:
            case List/Nil:
              return List/Cons(a, List/Cons(b, ys))
            case List/Cons:
              c = u.head
              v = u.tail
              match v:
                case List/Nil:
                  return List/Cons(a, List/Cons(b, List/Cons(c, ys)))
                case List/Cons:
                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(v.head, append4(v.tail, ys)))))
