def prog(xs):
  return map_inc(xs)

def map_inc(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      x1 = xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return List/Cons(x1 + 1, List/Nil)
        case List/Cons:
          x2 = t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Nil))
            case List/Cons:
              x3 = t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Nil)))
                case List/Cons:
                  x4 = t3.head
                  t4 = t3.tail
                  match t4:
                    case List/Nil:
                      return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Nil))))
                    case List/Cons:
                      x5 = t4.head
                      t5 = t4.tail
                      match t5:
                        case List/Nil:
                          return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Nil)))))
                        case List/Cons:
                          x6 = t5.head
                          t6 = t5.tail
                          match t6:
                            case List/Nil:
                              return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Nil))))))
                            case List/Cons:
                              x7 = t6.head
                              t7 = t6.tail
                              match t7:
                                case List/Nil:
                                  return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Cons(x7 + 1, List/Nil)))))))
                                case List/Cons:
                                  x8 = t7.head
                                  t8 = t7.tail
                                  match t8:
                                    case List/Nil:
                                      return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Cons(x7 + 1, List/Cons(x8 + 1, List/Nil))))))))
                                    case List/Cons:
                                      x9 = t8.head
                                      t9 = t8.tail
                                      match t9:
                                        case List/Nil:
                                          return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Cons(x7 + 1, List/Cons(x8 + 1, List/Cons(x9 + 1, List/Nil)))))))))
                                        case List/Cons:
                                          x10 = t9.head
                                          t10 = t9.tail
                                          match t10:
                                            case List/Nil:
                                              return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Cons(x7 + 1, List/Cons(x8 + 1, List/Cons(x9 + 1, List/Cons(x10 + 1, List/Nil))))))))))
                                            case List/Cons:
                                              x11 = t10.head
                                              t11 = t10.tail
                                              match t11:
                                                case List/Nil:
                                                  return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Cons(x7 + 1, List/Cons(x8 + 1, List/Cons(x9 + 1, List/Cons(x10 + 1, List/Cons(x11 + 1, List/Nil)))))))))))
                                                case List/Cons:
                                                  x12 = t11.head
                                                  t12 = t11.tail
                                                  match t12:
                                                    case List/Nil:
                                                      return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Cons(x7 + 1, List/Cons(x8 + 1, List/Cons(x9 + 1, List/Cons(x10 + 1, List/Cons(x11 + 1, List/Cons(x12 + 1, List/Nil))))))))))))
                                                    case List/Cons:
                                                      x13 = t12.head
                                                      t13 = t12.tail
                                                      match t13:
                                                        case List/Nil:
                                                          return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Cons(x7 + 1, List/Cons(x8 + 1, List/Cons(x9 + 1, List/Cons(x10 + 1, List/Cons(x11 + 1, List/Cons(x12 + 1, List/Cons(x13 + 1, List/Nil)))))))))))))
                                                        case List/Cons:
                                                          x14 = t13.head
                                                          t14 = t13.tail
                                                          match t14:
                                                            case List/Nil:
                                                              return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Cons(x7 + 1, List/Cons(x8 + 1, List/Cons(x9 + 1, List/Cons(x10 + 1, List/Cons(x11 + 1, List/Cons(x12 + 1, List/Cons(x13 + 1, List/Cons(x14 + 1, List/Nil))))))))))))))
                                                            case List/Cons:
                                                              x15 = t14.head
                                                              t15 = t14.tail
                                                              match t15:
                                                                case List/Nil:
                                                                  return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Cons(x7 + 1, List/Cons(x8 + 1, List/Cons(x9 + 1, List/Cons(x10 + 1, List/Cons(x11 + 1, List/Cons(x12 + 1, List/Cons(x13 + 1, List/Cons(x14 + 1, List/Cons(x15 + 1, List/Nil)))))))))))))))
                                                                case List/Cons:
                                                                  x16 = t15.head
                                                                  return List/Cons(x1 + 1, List/Cons(x2 + 1, List/Cons(x3 + 1, List/Cons(x4 + 1, List/Cons(x5 + 1, List/Cons(x6 + 1, List/Cons(x7 + 1, List/Cons(x8 + 1, List/Cons(x9 + 1, List/Cons(x10 + 1, List/Cons(x11 + 1, List/Cons(x12 + 1, List/Cons(x13 + 1, List/Cons(x14 + 1, List/Cons(x15 + 1, List/Cons(x16 + 1, map_inc(t15.tail))))))))))))))))
