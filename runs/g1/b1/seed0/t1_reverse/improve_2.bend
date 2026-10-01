def prog(xs):
  return reverse_blocks(xs, [])

def reverse_blocks(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      a = xs.head
      ys = xs.tail
      match ys:
        case List/Nil:
          return List/Cons(a, acc)
        case List/Cons:
          b = ys.head
          zs = ys.tail
          match zs:
            case List/Nil:
              return List/Cons(b, List/Cons(a, acc))
            case List/Cons:
              c = zs.head
              ws = zs.tail
              match ws:
                case List/Nil:
                  return List/Cons(c, List/Cons(b, List/Cons(a, acc)))
                case List/Cons:
                  d = ws.head
                  vs = ws.tail
                  match vs:
                    case List/Nil:
                      return List/Cons(d, List/Cons(c, List/Cons(b, List/Cons(a, acc))))
                    case List/Cons:
                      e = vs.head
                      us = vs.tail
                      match us:
                        case List/Nil:
                          return List/Cons(e, List/Cons(d, List/Cons(c, List/Cons(b, List/Cons(a, acc)))))
                        case List/Cons:
                          f = us.head
                          ts = us.tail
                          match ts:
                            case List/Nil:
                              return List/Cons(f, List/Cons(e, List/Cons(d, List/Cons(c, List/Cons(b, List/Cons(a, acc))))))
                            case List/Cons:
                              g = ts.head
                              rs = ts.tail
                              match rs:
                                case List/Nil:
                                  return List/Cons(g, List/Cons(f, List/Cons(e, List/Cons(d, List/Cons(c, List/Cons(b, List/Cons(a, acc)))))))
                                case List/Cons:
                                  h = rs.head
                                  rest = rs.tail
                                  return reverse_blocks(rest, List/Cons(h, List/Cons(g, List/Cons(f, List/Cons(e, List/Cons(d, List/Cons(c, List/Cons(b, List/Cons(a, acc)))))))))
