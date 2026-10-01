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
                                  return a + b + c + d + e + f + g + h + sum_list(t8)
