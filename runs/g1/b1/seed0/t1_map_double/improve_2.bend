def prog(xs):
  return map_block(xs)

def map_linear(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      return List/Cons(xs.head * 2, map_linear(xs.tail))

def map_block(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      a = xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return map_linear(xs)
        case List/Cons:
          b = t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return map_linear(xs)
            case List/Cons:
              c = t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return map_linear(xs)
                case List/Cons:
                  d = t3.head
                  t4 = t3.tail
                  match t4:
                    case List/Nil:
                      return map_linear(xs)
                    case List/Cons:
                      e = t4.head
                      t5 = t4.tail
                      match t5:
                        case List/Nil:
                          return map_linear(xs)
                        case List/Cons:
                          f = t5.head
                          t6 = t5.tail
                          match t6:
                            case List/Nil:
                              return map_linear(xs)
                            case List/Cons:
                              g = t6.head
                              t7 = t6.tail
                              match t7:
                                case List/Nil:
                                  return map_linear(xs)
                                case List/Cons:
                                  h = t7.head
                                  t8 = t7.tail
                                  match t8:
                                    case List/Nil:
                                      return map_linear(xs)
                                    case List/Cons:
                                      i = t8.head
                                      t9 = t8.tail
                                      match t9:
                                        case List/Nil:
                                          return map_linear(xs)
                                        case List/Cons:
                                          j = t9.head
                                          t10 = t9.tail
                                          match t10:
                                            case List/Nil:
                                              return map_linear(xs)
                                            case List/Cons:
                                              k = t10.head
                                              t11 = t10.tail
                                              match t11:
                                                case List/Nil:
                                                  return map_linear(xs)
                                                case List/Cons:
                                                  l = t11.head
                                                  t12 = t11.tail
                                                  match t12:
                                                    case List/Nil:
                                                      return map_linear(xs)
                                                    case List/Cons:
                                                      m = t12.head
                                                      t13 = t12.tail
                                                      match t13:
                                                        case List/Nil:
                                                          return map_linear(xs)
                                                        case List/Cons:
                                                          n = t13.head
                                                          t14 = t13.tail
                                                          match t14:
                                                            case List/Nil:
                                                              return map_linear(xs)
                                                            case List/Cons:
                                                              o = t14.head
                                                              t15 = t14.tail
                                                              match t15:
                                                                case List/Nil:
                                                                  return map_linear(xs)
                                                                case List/Cons:
                                                                  p = t15.head
                                                                  t16 = t15.tail
                                                                  return List/Cons(a * 2, List/Cons(b * 2, List/Cons(c * 2, List/Cons(d * 2, List/Cons(e * 2, List/Cons(f * 2, List/Cons(g * 2, List/Cons(h * 2, List/Cons(i * 2, List/Cons(j * 2, List/Cons(k * 2, List/Cons(l * 2, List/Cons(m * 2, List/Cons(n * 2, List/Cons(o * 2, List/Cons(p * 2, map_block(t16))))))))))))))))))
