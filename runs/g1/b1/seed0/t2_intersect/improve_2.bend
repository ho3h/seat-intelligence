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
            return List/Cons(xs.head, intersect(xs.tail, ys.tail))
          else:
            if xs.head < ys.head:
              return intersect(skip_to(xs.tail, ys.head), ys)
            else:
              return intersect(skip_to(ys.tail, xs.head), xs)

def skip_to(xs, pivot):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head >= pivot:
        return xs
      else:
        a = xs.tail
        match a:
          case List/Nil:
            return []
          case List/Cons:
            if a.head >= pivot:
              return a
            else:
              b = a.tail
              match b:
                case List/Nil:
                  return []
                case List/Cons:
                  if b.head >= pivot:
                    return b
                  else:
                    c = b.tail
                    match c:
                      case List/Nil:
                        return []
                      case List/Cons:
                        if c.head >= pivot:
                          return c
                        else:
                          return skip_to(c.tail, pivot)
