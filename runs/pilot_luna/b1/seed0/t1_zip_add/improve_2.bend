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
                                  xt4 = xt3.tail
                                  yt4 = yt3.tail
                                  match xt4:
                                    case List/Nil:
                                      return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, []))))
                                    case List/Cons:
                                      match yt4:
                                        case List/Nil:
                                          return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, []))))
                                        case List/Cons:
                                          e = xt4.head + yt4.head
                                          xt5 = xt4.tail
                                          yt5 = yt4.tail
                                          match xt5:
                                            case List/Nil:
                                              return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, [])))))
                                            case List/Cons:
                                              match yt5:
                                                case List/Nil:
                                                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, [])))))
                                                case List/Cons:
                                                  f = xt5.head + yt5.head
                                                  xt6 = xt5.tail
                                                  yt6 = yt5.tail
                                                  match xt6:
                                                    case List/Nil:
                                                      return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, []))))))
                                                    case List/Cons:
                                                      match yt6:
                                                        case List/Nil:
                                                          return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, []))))))
                                                        case List/Cons:
                                                          g = xt6.head + yt6.head
                                                          xt7 = xt6.tail
                                                          yt7 = yt6.tail
                                                          match xt7:
                                                            case List/Nil:
                                                              return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, List/Cons(g, [])))))))
                                                            case List/Cons:
                                                              match yt7:
                                                                case List/Nil:
                                                                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, List/Cons(g, [])))))))
                                                                case List/Cons:
                                                                  h = xt7.head + yt7.head
                                                                  tail = zip_add(xt7.tail, yt7.tail)
                                                                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, List/Cons(g, List/Cons(h, tail))))))))
