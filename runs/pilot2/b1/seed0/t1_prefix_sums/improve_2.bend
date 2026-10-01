def prog(x):
  return prefix16(x, 0)

def prefix16(xs, acc):
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
                                  t8 = t7.tail
                                  match t8:
                                    case List/Nil:
                                      return [a0, a1, a2, a3, a4, a5, a6, a7]
                                    case List/Cons:
                                      a8 = a7 + t8.head
                                      t9 = t8.tail
                                      match t9:
                                        case List/Nil:
                                          return [a0, a1, a2, a3, a4, a5, a6, a7, a8]
                                        case List/Cons:
                                          a9 = a8 + t9.head
                                          t10 = t9.tail
                                          match t10:
                                            case List/Nil:
                                              return [a0, a1, a2, a3, a4, a5, a6, a7, a8, a9]
                                            case List/Cons:
                                              a10 = a9 + t10.head
                                              t11 = t10.tail
                                              match t11:
                                                case List/Nil:
                                                  return [a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10]
                                                case List/Cons:
                                                  a11 = a10 + t11.head
                                                  t12 = t11.tail
                                                  match t12:
                                                    case List/Nil:
                                                      return [a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11]
                                                    case List/Cons:
                                                      a12 = a11 + t12.head
                                                      t13 = t12.tail
                                                      match t13:
                                                        case List/Nil:
                                                          return [a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12]
                                                        case List/Cons:
                                                          a13 = a12 + t13.head
                                                          t14 = t13.tail
                                                          match t14:
                                                            case List/Nil:
                                                              return [a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13]
                                                            case List/Cons:
                                                              a14 = a13 + t14.head
                                                              t15 = t14.tail
                                                              match t15:
                                                                case List/Nil:
                                                                  return [a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14]
                                                                case List/Cons:
                                                                  a15 = a14 + t15.head
                                                                  return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, List/Cons(a6, List/Cons(a7, List/Cons(a8, List/Cons(a9, List/Cons(a10, List/Cons(a11, List/Cons(a12, List/Cons(a13, List/Cons(a14, List/Cons(a15, prefix16(t15.tail, a15))))))))))))))))
