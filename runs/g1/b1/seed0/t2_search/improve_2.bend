def prog(x):
  (xs, t) = x
  return search8(xs, t, 0)

def search8(xs, t, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      a = xs.tail
      match a:
        case List/Nil:
          return linear(xs, t, i)
        case List/Cons:
          b = a.tail
          match b:
            case List/Nil:
              return linear(xs, t, i)
            case List/Cons:
              c = b.tail
              match c:
                case List/Nil:
                  return linear(xs, t, i)
                case List/Cons:
                  d = c.tail
                  match d:
                    case List/Nil:
                      return linear(xs, t, i)
                    case List/Cons:
                      e = d.tail
                      match e:
                        case List/Nil:
                          return linear(xs, t, i)
                        case List/Cons:
                          f = e.tail
                          match f:
                            case List/Nil:
                              return linear(xs, t, i)
                            case List/Cons:
                              g = f.tail
                              match g:
                                case List/Nil:
                                  return linear(xs, t, i)
                                case List/Cons:
                                  if g.head < t:
                                    return search8(g.tail, t, i + 8)
                                  else:
                                    return linear(xs, t, i)

def linear(xs, t, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      if xs.head == t:
        return i
      else:
        if xs.head > t:
          return 16777215
        else:
          return linear(xs.tail, t, i + 1)
