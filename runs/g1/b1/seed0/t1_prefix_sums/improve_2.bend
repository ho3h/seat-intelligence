def prog(xs):
  return scan(xs, 0)

def scan(xs, acc):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      a = acc + xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return List/Cons(a, List/Nil)
        case List/Cons:
          b = a + t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return List/Cons(a, List/Cons(b, List/Nil))
            case List/Cons:
              c = b + t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Nil)))
                case List/Cons:
                  d = c + t3.head
                  t4 = t3.tail
                  match t4:
                    case List/Nil:
                      return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Nil))))
                    case List/Cons:
                      e = d + t4.head
                      t5 = t4.tail
                      match t5:
                        case List/Nil:
                          return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Nil)))))
                        case List/Cons:
                          f = e + t5.head
                          t6 = t5.tail
                          match t6:
                            case List/Nil:
                              return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, List/Nil))))))
                            case List/Cons:
                              g = f + t6.head
                              t7 = t6.tail
                              match t7:
                                case List/Nil:
                                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, List/Cons(g, List/Nil)))))))
                                case List/Cons:
                                  h = g + t7.head
                                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, List/Cons(e, List/Cons(f, List/Cons(g, List/Cons(h, scan(t7.tail, h))))))))
