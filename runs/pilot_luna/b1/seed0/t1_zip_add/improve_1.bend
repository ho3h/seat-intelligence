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
                  xt2 = xt.tail
                  yt2 = yt.tail
                  match xt2:
                    case List/Nil:
                      return List/Cons(a, List/Cons(b, []))
                    case List/Cons:
                      match yt2:
                        case List/Nil:
                          return List/Cons(a, List/Cons(b, []))
                        case List/Cons:
                          c = xt2.head + yt2.head
                          xt3 = xt2.tail
                          yt3 = yt2.tail
                          match xt3:
                            case List/Nil:
                              return List/Cons(a, List/Cons(b, List/Cons(c, [])))
                            case List/Cons:
                              match yt3:
                                case List/Nil:
                                  return List/Cons(a, List/Cons(b, List/Cons(c, [])))
                                case List/Cons:
                                  d = xt3.head + yt3.head
                                  tail = zip_add(xt3.tail, yt3.tail)
                                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, tail))))
