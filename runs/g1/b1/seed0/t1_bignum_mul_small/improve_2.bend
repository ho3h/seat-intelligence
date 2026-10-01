def prog(x):
  (a, k) = x
  if k == 0:
    return []
  else:
    return mul_digits(a, k, 0)

def carry_list(c):
  if c == 0:
    return []
  else:
    return [c]

def mul_digits(xs, k, carry):
  match xs:
    case List/Nil:
      return carry_list(carry)
    case List/Cons:
      v1 = xs.head * k + carry
      d1 = v1 & 4095
      c1 = v1 >> 12
      r1 = xs.tail
      match r1:
        case List/Nil:
          return List/Cons(d1, carry_list(c1))
        case List/Cons:
          v2 = r1.head * k + c1
          d2 = v2 & 4095
          c2 = v2 >> 12
          r2 = r1.tail
          match r2:
            case List/Nil:
              return List/Cons(d1, List/Cons(d2, carry_list(c2)))
            case List/Cons:
              v3 = r2.head * k + c2
              d3 = v3 & 4095
              c3 = v3 >> 12
              r3 = r2.tail
              match r3:
                case List/Nil:
                  return List/Cons(d1, List/Cons(d2, List/Cons(d3, carry_list(c3))))
                case List/Cons:
                  v4 = r3.head * k + c3
                  d4 = v4 & 4095
                  c4 = v4 >> 12
                  r4 = r3.tail
                  match r4:
                    case List/Nil:
                      return List/Cons(d1, List/Cons(d2, List/Cons(d3, List/Cons(d4, carry_list(c4)))))
                    case List/Cons:
                      v5 = r4.head * k + c4
                      d5 = v5 & 4095
                      c5 = v5 >> 12
                      r5 = r4.tail
                      match r5:
                        case List/Nil:
                          return List/Cons(d1, List/Cons(d2, List/Cons(d3, List/Cons(d4, List/Cons(d5, carry_list(c5))))))
                        case List/Cons:
                          v6 = r5.head * k + c5
                          d6 = v6 & 4095
                          c6 = v6 >> 12
                          r6 = r5.tail
                          match r6:
                            case List/Nil:
                              return List/Cons(d1, List/Cons(d2, List/Cons(d3, List/Cons(d4, List/Cons(d5, List/Cons(d6, carry_list(c6)))))))
                            case List/Cons:
                              v7 = r6.head * k + c6
                              d7 = v7 & 4095
                              c7 = v7 >> 12
                              r7 = r6.tail
                              match r7:
                                case List/Nil:
                                  return List/Cons(d1, List/Cons(d2, List/Cons(d3, List/Cons(d4, List/Cons(d5, List/Cons(d6, List/Cons(d7, carry_list(c7))))))))
                                case List/Cons:
                                  v8 = r7.head * k + c7
                                  d8 = v8 & 4095
                                  c8 = v8 >> 12
                                  return List/Cons(d1, List/Cons(d2, List/Cons(d3, List/Cons(d4, List/Cons(d5, List/Cons(d6, List/Cons(d7, List/Cons(d8, mul_digits(r7.tail, k, c8)))))))))
