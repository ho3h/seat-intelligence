def prog(x):
  (k, xs) = x
  return drop_fast(k, xs)

def drop_fast(k, xs):
  if k < 8:
    return drop_small(k, xs)
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        a = xs.tail
        match a:
          case List/Nil:
            return []
          case List/Cons:
            b = a.tail
            match b:
              case List/Nil:
                return []
              case List/Cons:
                c = b.tail
                match c:
                  case List/Nil:
                    return []
                  case List/Cons:
                    d = c.tail
                    match d:
                      case List/Nil:
                        return []
                      case List/Cons:
                        e = d.tail
                        match e:
                          case List/Nil:
                            return []
                          case List/Cons:
                            f = e.tail
                            match f:
                              case List/Nil:
                                return []
                              case List/Cons:
                                g = f.tail
                                match g:
                                  case List/Nil:
                                    return []
                                  case List/Cons:
                                    return drop_fast(k - 8, g.tail)

def drop_small(k, xs):
  switch k:
    case 0:
      return xs
    case _:
      match xs:
        case List/Nil:
          return []
        case List/Cons:
          return drop_small(k - 1, xs.tail)
