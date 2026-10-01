def prog(x):
  (k, xs) = x
  return take(k, xs)

def take(k, xs):
  if k >= 16:
    return take16(k, xs)
  else:
    if k >= 8:
      return take8(k, xs)
    else:
      return take_small(k, xs)

def take_small(k, xs):
  if k == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(xs.head, take_small(k - 1, xs.tail))

def take8(k, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a = xs.tail
      match a:
        case List/Nil:
          return [xs.head]
        case List/Cons:
          b = a.tail
          match b:
            case List/Nil:
              return [xs.head, a.head]
            case List/Cons:
              c = b.tail
              match c:
                case List/Nil:
                  return [xs.head, a.head, b.head]
                case List/Cons:
                  d = c.tail
                  match d:
                    case List/Nil:
                      return [xs.head, a.head, b.head, c.head]
                    case List/Cons:
                      e = d.tail
                      match e:
                        case List/Nil:
                          return [xs.head, a.head, b.head, c.head, d.head]
                        case List/Cons:
                          f = e.tail
                          match f:
                            case List/Nil:
                              return [xs.head, a.head, b.head, c.head, d.head, e.head]
                            case List/Cons:
                              g = f.tail
                              match g:
                                case List/Nil:
                                  return [xs.head, a.head, b.head, c.head, d.head, e.head, f.head]
                                case List/Cons:
                                  return prepend8(xs.head, a.head, b.head, c.head, d.head, e.head, f.head, g.head, take(k - 8, g.tail))

def take16(k, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a = xs.tail
      match a:
        case List/Nil:
          return [xs.head]
        case List/Cons:
          b = a.tail
          match b:
            case List/Nil:
              return [xs.head, a.head]
            case List/Cons:
              c = b.tail
              match c:
                case List/Nil:
                  return [xs.head, a.head, b.head]
                case List/Cons:
                  d = c.tail
                  match d:
                    case List/Nil:
                      return [xs.head, a.head, b.head, c.head]
                    case List/Cons:
                      e = d.tail
                      match e:
                        case List/Nil:
                          return [xs.head, a.head, b.head, c.head, d.head]
                        case List/Cons:
                          f = e.tail
                          match f:
                            case List/Nil:
                              return [xs.head, a.head, b.head, c.head, d.head, e.head]
                            case List/Cons:
                              g = f.tail
                              match g:
                                case List/Nil:
                                  return [xs.head, a.head, b.head, c.head, d.head, e.head, f.head]
                                case List/Cons:
                                  return take16b(k, xs.head, a.head, b.head, c.head, d.head, e.head, f.head, g.head, g.tail)

def take16b(k, p0, p1, p2, p3, p4, p5, p6, p7, xs):
  match xs:
    case List/Nil:
      return prepend8(p0, p1, p2, p3, p4, p5, p6, p7, [])
    case List/Cons:
      a = xs.tail
      match a:
        case List/Nil:
          return prepend8(p0, p1, p2, p3, p4, p5, p6, p7, [xs.head])
        case List/Cons:
          b = a.tail
          match b:
            case List/Nil:
              return prepend8(p0, p1, p2, p3, p4, p5, p6, p7, [xs.head, a.head])
            case List/Cons:
              c = b.tail
              match c:
                case List/Nil:
                  return prepend8(p0, p1, p2, p3, p4, p5, p6, p7, [xs.head, a.head, b.head])
                case List/Cons:
                  d = c.tail
                  match d:
                    case List/Nil:
                      return prepend8(p0, p1, p2, p3, p4, p5, p6, p7, [xs.head, a.head, b.head, c.head])
                    case List/Cons:
                      e = d.tail
                      match e:
                        case List/Nil:
                          return prepend8(p0, p1, p2, p3, p4, p5, p6, p7, [xs.head, a.head, b.head, c.head, d.head])
                        case List/Cons:
                          f = e.tail
                          match f:
                            case List/Nil:
                              return prepend8(p0, p1, p2, p3, p4, p5, p6, p7, [xs.head, a.head, b.head, c.head, d.head, e.head])
                            case List/Cons:
                              g = f.tail
                              match g:
                                case List/Nil:
                                  return prepend8(p0, p1, p2, p3, p4, p5, p6, p7, [xs.head, a.head, b.head, c.head, d.head, e.head, f.head])
                                case List/Cons:
                                  return prepend8(p0, p1, p2, p3, p4, p5, p6, p7, prepend8(xs.head, a.head, b.head, c.head, d.head, e.head, f.head, g.head, take(k - 16, g.tail)))

def prepend8(a, b, c, d, e, f, g, h, tail):
  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, List/Cons(g, List/Cons(h, tail))))))))
