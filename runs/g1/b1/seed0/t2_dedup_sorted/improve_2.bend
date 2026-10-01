def prog(xs):
  return dedup(xs, 0)

def prepend_if(xs, value, keep):
  if keep:
    return List/Cons(value, xs)
  else:
    return xs

def one(xs, prev):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      return prepend_if(dedup(xs.tail, xs.head), xs.head, xs.head != prev)

def dedup(xs, prev):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a = xs.head
      match xs.tail:
        case List/Nil:
          return one(xs, prev)
        case List/Cons:
          b = xs.tail.head
          match xs.tail.tail:
            case List/Nil:
              return one(xs, prev)
            case List/Cons:
              c = xs.tail.tail.head
              match xs.tail.tail.tail:
                case List/Nil:
                  return one(xs, prev)
                case List/Cons:
                  d = xs.tail.tail.tail.head
                  match xs.tail.tail.tail.tail:
                    case List/Nil:
                      return one(xs, prev)
                    case List/Cons:
                      e = xs.tail.tail.tail.tail.head
                      match xs.tail.tail.tail.tail.tail:
                        case List/Nil:
                          return one(xs, prev)
                        case List/Cons:
                          f = xs.tail.tail.tail.tail.tail.head
                          match xs.tail.tail.tail.tail.tail.tail:
                            case List/Nil:
                              return one(xs, prev)
                            case List/Cons:
                              g = xs.tail.tail.tail.tail.tail.tail.head
                              match xs.tail.tail.tail.tail.tail.tail.tail:
                                case List/Nil:
                                  return one(xs, prev)
                                case List/Cons:
                                  h = xs.tail.tail.tail.tail.tail.tail.tail.head
                                  rest = dedup(xs.tail.tail.tail.tail.tail.tail.tail.tail.tail, h)
                                  r1 = prepend_if(rest, h, h != g)
                                  r2 = prepend_if(r1, g, g != f)
                                  r3 = prepend_if(r2, f, f != e)
                                  r4 = prepend_if(r3, e, e != d)
                                  r5 = prepend_if(r4, d, d != c)
                                  r6 = prepend_if(r5, c, c != b)
                                  r7 = prepend_if(r6, b, b != a)
                                  return prepend_if(r7, a, a != prev)
