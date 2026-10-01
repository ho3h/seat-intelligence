def prog(xs):
  return length(xs)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      a = xs.tail
      match a:
        case List/Nil:
          return 1
        case List/Cons:
          b = a.tail
          match b:
            case List/Nil:
              return 2
            case List/Cons:
              c = b.tail
              match c:
                case List/Nil:
                  return 3
                case List/Cons:
                  d = c.tail
                  match d:
                    case List/Nil:
                      return 4
                    case List/Cons:
                      e = d.tail
                      match e:
                        case List/Nil:
                          return 5
                        case List/Cons:
                          f = e.tail
                          match f:
                            case List/Nil:
                              return 6
                            case List/Cons:
                              g = f.tail
                              match g:
                                case List/Nil:
                                  return 7
                                case List/Cons:
                                  return 8 + length(g.tail)
