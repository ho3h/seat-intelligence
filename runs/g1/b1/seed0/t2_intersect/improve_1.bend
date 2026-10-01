def prog(x):
  (xs, ys) = x
  return intersect(xs, ys)

def intersect(xs, ys):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match ys:
        case List/Nil:
          return []
        case List/Cons:
          if xs.head == ys.head:
            a = xs.head
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
                    if xt.head == yt.head:
                      return List/Cons(a, List/Cons(xt.head, intersect(xt.tail, yt.tail)))
                    else:
                      if xt.head < yt.head:
                        return List/Cons(a, intersect(xt.tail, yt))
                      else:
                        return List/Cons(a, intersect(xt, yt.tail))
          else:
            if xs.head < ys.head:
              xt = xs.tail
              match xt:
                case List/Nil:
                  return []
                case List/Cons:
                  if xt.head == ys.head:
                    return List/Cons(ys.head, intersect(xt.tail, ys.tail))
                  else:
                    if xt.head < ys.head:
                      return intersect(xt.tail, ys)
                    else:
                      return intersect(xt, ys.tail)
            else:
              yt = ys.tail
              match yt:
                case List/Nil:
                  return []
                case List/Cons:
                  if xs.head == yt.head:
                    return List/Cons(xs.head, intersect(xs.tail, yt.tail))
                  else:
                    if xs.head < yt.head:
                      return intersect(xs.tail, yt)
                    else:
                      return intersect(xs, yt.tail)
