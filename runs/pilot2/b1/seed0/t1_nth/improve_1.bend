def prog(x):
  (i, xs) = x
  return nth(i, xs)

def nth(i, xs):
  if i < 16:
    return nth_small(i, xs)
  else:
    rest = drop16(xs)
    match rest:
      case List/Nil:
        return 0
      case List/Cons:
        return nth(i - 16, rest)

def nth_small(i, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return nth_small(i - 1, xs.tail)

def drop16(xs):
  first = drop8(xs)
  return drop8(first)

def drop8(xs):
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
                                  return g.tail
