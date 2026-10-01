def prog(xs):
  return max_list(xs)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

def max4(a, b, c, d):
  return max2(max2(a, b), max2(c, d))

def max8(a, b, c, d, e, f, g, h):
  return max2(max4(a, b, c, d), max4(e, f, g, h))

def max_list(xs):
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
              return max2(a, b)
            case List/Cons:
              c = t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return max2(max2(a, b), c)
                case List/Cons:
                  d = t3.head
                  t4 = t3.tail
                  match t4:
                    case List/Nil:
                      return max4(a, b, c, d)
                    case List/Cons:
                      e = t4.head
                      t5 = t4.tail
                      match t5:
                        case List/Nil:
                          return max2(max4(a, b, c, d), e)
                        case List/Cons:
                          f = t5.head
                          t6 = t5.tail
                          match t6:
                            case List/Nil:
                              return max2(max4(a, b, c, d), max2(e, f))
                            case List/Cons:
                              g = t6.head
                              t7 = t6.tail
                              match t7:
                                case List/Nil:
                                  return max2(max4(a, b, c, d), max2(max2(e, f), g))
                                case List/Cons:
                                  h = t7.head
                                  t8 = t7.tail
                                  return max2(max8(a, b, c, d, e, f, g, h), max_list(t8))
