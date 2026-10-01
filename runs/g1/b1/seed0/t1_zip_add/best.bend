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
          a0 = xs.head + ys.head
          xt1 = xs.tail
          yt1 = ys.tail
          match xt1:
            case List/Nil:
              return List/Cons(a0, [])
            case List/Cons:
              match yt1:
                case List/Nil:
                  return List/Cons(a0, [])
                case List/Cons:
                  a1 = xt1.head + yt1.head
                  xt2 = xt1.tail
                  yt2 = yt1.tail
                  match xt2:
                    case List/Nil:
                      return List/Cons(a0, List/Cons(a1, []))
                    case List/Cons:
                      match yt2:
                        case List/Nil:
                          return List/Cons(a0, List/Cons(a1, []))
                        case List/Cons:
                          a2 = xt2.head + yt2.head
                          xt3 = xt2.tail
                          yt3 = yt2.tail
                          match xt3:
                            case List/Nil:
                              return List/Cons(a0, List/Cons(a1, List/Cons(a2, [])))
                            case List/Cons:
                              match yt3:
                                case List/Nil:
                                  return List/Cons(a0, List/Cons(a1, List/Cons(a2, [])))
                                case List/Cons:
                                  a3 = xt3.head + yt3.head
                                  rest = zip_add(xt3.tail, yt3.tail)
                                  return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, rest))))
