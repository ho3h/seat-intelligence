def prog(x):
  (xs, t) = x
  return lb4(xs, t)

def lb4(xs, t):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head < t:
        a = xs.tail
        match a:
          case List/Nil:
            return 1
          case List/Cons:
            if a.head < t:
              b = a.tail
              match b:
                case List/Nil:
                  return 2
                case List/Cons:
                  if b.head < t:
                    c = b.tail
                    match c:
                      case List/Nil:
                        return 3
                      case List/Cons:
                        if c.head < t:
                          return 4 + lb4(c.tail, t)
                        else:
                          return 3
                  else:
                    return 2
            else:
              return 1
      else:
        return 0
