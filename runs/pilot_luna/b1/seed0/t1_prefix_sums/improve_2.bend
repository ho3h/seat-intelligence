def prog(xs):
  return scan8(xs, 0)

def scan8(xs, acc):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      a1 = acc + xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return List/Cons(a1, List/Nil)
        case List/Cons:
          a2 = a1 + t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return List/Cons(a1, List/Cons(a2, List/Nil))
            case List/Cons:
              a3 = a2 + t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Nil)))
                case List/Cons:
                  a4 = a3 + t3.head
                  t4 = t3.tail
                  match t4:
                    case List/Nil:
                      return List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Nil))))
                    case List/Cons:
                      a5 = a4 + t4.head
                      t5 = t4.tail
                      match t5:
                        case List/Nil:
                          return List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, List/Nil)))))
                        case List/Cons:
                          a6 = a5 + t5.head
                          t6 = t5.tail
                          match t6:
                            case List/Nil:
                              return List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, List/Cons(a6, List/Nil))))))
                            case List/Cons:
                              a7 = a6 + t6.head
                              t7 = t6.tail
                              match t7:
                                case List/Nil:
                                  return List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, List/Cons(a6, List/Cons(a7, List/Nil)))))))
                                case List/Cons:
                                  a8 = a7 + t7.head
                                  suffix = scan8(t7.tail, a8)
                                  return List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, List/Cons(a6, List/Cons(a7, List/Cons(a8, suffix))))))))
