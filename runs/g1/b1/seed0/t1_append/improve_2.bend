def prog(x):
  (xs, ys) = x
  return append8(xs, ys)

def append8(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      a = xs.head
      t = xs.tail
      match t:
        case List/Nil:
          return List/Cons(a, ys)
        case List/Cons:
          b = t.head
          u = t.tail
          match u:
            case List/Nil:
              return List/Cons(a, List/Cons(b, ys))
            case List/Cons:
              c = u.head
              v = u.tail
              match v:
                case List/Nil:
                  return List/Cons(a, List/Cons(b, List/Cons(c, ys)))
                case List/Cons:
                  d = v.head
                  w = v.tail
                  match w:
                    case List/Nil:
                      return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, ys))))
                    case List/Cons:
                      e = w.head
                      r = w.tail
                      match r:
                        case List/Nil:
                          return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, ys)))))
                        case List/Cons:
                          f = r.head
                          s = r.tail
                          match s:
                            case List/Nil:
                              return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, ys))))))
                            case List/Cons:
                              g = s.head
                              q = s.tail
                              match q:
                                case List/Nil:
                                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, List/Cons(g, ys)))))))
                                case List/Cons:
                                  h = q.head
                                  z = q.tail
                                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, List/Cons(g, List/Cons(h, append8(z, ys)))))))))
