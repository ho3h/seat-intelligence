def prog(xs):
  return sum_list(xs)

def sum_list(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      a = xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return a
        case List/Cons:
          b = t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return a + b
            case List/Cons:
              c = t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return a + b + c
                case List/Cons:
                  d = t3.head
                  t4 = t3.tail
                  match t4:
                    case List/Nil:
                      return a + b + c + d
                    case List/Cons:
                      e = t4.head
                      t5 = t4.tail
                      match t5:
                        case List/Nil:
                          return a + b + c + d + e
                        case List/Cons:
                          f = t5.head
                          t6 = t5.tail
                          match t6:
                            case List/Nil:
                              return a + b + c + d + e + f
                            case List/Cons:
                              g = t6.head
                              t7 = t6.tail
                              match t7:
                                case List/Nil:
                                  return a + b + c + d + e + f + g
                                case List/Cons:
                                  h = t7.head
                                  t8 = t7.tail
                                  match t8:
                                    case List/Nil:
                                      return a + b + c + d + e + f + g + h
                                    case List/Cons:
                                      i = t8.head
                                      t9 = t8.tail
                                      match t9:
                                        case List/Nil:
                                          return a + b + c + d + e + f + g + h + i
                                        case List/Cons:
                                          j = t9.head
                                          t10 = t9.tail
                                          match t10:
                                            case List/Nil:
                                              return a + b + c + d + e + f + g + h + i + j
                                            case List/Cons:
                                              k = t10.head
                                              t11 = t10.tail
                                              match t11:
                                                case List/Nil:
                                                  return a + b + c + d + e + f + g + h + i + j + k
                                                case List/Cons:
                                                  l = t11.head
                                                  t12 = t11.tail
                                                  match t12:
                                                    case List/Nil:
                                                      return a + b + c + d + e + f + g + h + i + j + k + l
                                                    case List/Cons:
                                                      m = t12.head
                                                      t13 = t12.tail
                                                      match t13:
                                                        case List/Nil:
                                                          return a + b + c + d + e + f + g + h + i + j + k + l + m
                                                        case List/Cons:
                                                          n = t13.head
                                                          t14 = t13.tail
                                                          match t14:
                                                            case List/Nil:
                                                              return a + b + c + d + e + f + g + h + i + j + k + l + m + n
                                                            case List/Cons:
                                                              o = t14.head
                                                              t15 = t14.tail
                                                              match t15:
                                                                case List/Nil:
                                                                  return a + b + c + d + e + f + g + h + i + j + k + l + m + n + o
                                                                case List/Cons:
                                                                  p = t15.head
                                                                  t16 = t15.tail
                                                                  return a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p + sum_list(t16)
