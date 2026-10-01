def prog(x):
  (xs, ys) = x
  return zip_add(xs, ys)

def zip_add(xs, ys):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match ys:
        case List/Nil:
          return []
        case List/Cons:
          a = xs.head + ys.head
          xt = xs.tail
          yt = ys.tail
          match xt:
            case List/Nil:
              return List/Cons(a, [])
            case List/Cons:
              match yt:
                case List/Nil:
                  return List/Cons(a, [])
                case List/Cons:
                  b = xt.head + yt.head
                  rest = zip_add(xt.tail, yt.tail)
                  return List/Cons(a, List/Cons(b, rest))
