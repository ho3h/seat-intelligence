def prog(x):
  return prefix8(x, 0)

def prefix8(xs, acc):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a0 = acc + xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return [a0]
        case List/Cons:
          a1 = a0 + t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return [a0, a1]
            case List/Cons:
              a2 = a1 + t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return [a0, a1, a2]
                case List/Cons:
                  a3 = a2 + t3.head
                  t4 = t3.tail
                  match t4:
                    case List/Nil:
                      return [a0, a1, a2, a3]
                    case List/Cons:
                      a4 = a3 + t4.head
                      t5 = t4.tail
                      match t5:
                        case List/Nil:
                          return [a0, a1, a2, a3, a4]
                        case List/Cons:
                          a5 = a4 + t5.head
                          t6 = t5.tail
                          match t6:
                            case List/Nil:
                              return [a0, a1, a2, a3, a4, a5]
                            case List/Cons:
                              a6 = a5 + t6.head
                              t7 = t6.tail
                              match t7:
                                case List/Nil:
                                  return [a0, a1, a2, a3, a4, a5, a6]
                                case List/Cons:
                                  a7 = a6 + t7.head
                                  return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, List/Cons(a6, List/Cons(a7, prefix8(t7.tail, a7)))))))))
