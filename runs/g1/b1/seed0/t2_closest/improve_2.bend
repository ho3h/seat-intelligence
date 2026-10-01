def prog(input):
  (x, xs) = input
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      d = absdiff(xs.head, x)
      return scan16(xs.tail, x, xs.head, d)

def scan16(xs, x, best, best_dist):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      (b1, d1) = pick(xs.head, x, best, best_dist)
      r1 = xs.tail
      match r1:
        case List/Nil:
          return b1
        case List/Cons:
          (b2, d2) = pick(r1.head, x, b1, d1)
          r2 = r1.tail
          match r2:
            case List/Nil:
              return b2
            case List/Cons:
              (b3, d3) = pick(r2.head, x, b2, d2)
              r3 = r2.tail
              match r3:
                case List/Nil:
                  return b3
                case List/Cons:
                  (b4, d4) = pick(r3.head, x, b3, d3)
                  r4 = r3.tail
                  match r4:
                    case List/Nil:
                      return b4
                    case List/Cons:
                      (b5, d5) = pick(r4.head, x, b4, d4)
                      r5 = r4.tail
                      match r5:
                        case List/Nil:
                          return b5
                        case List/Cons:
                          (b6, d6) = pick(r5.head, x, b5, d5)
                          r6 = r5.tail
                          match r6:
                            case List/Nil:
                              return b6
                            case List/Cons:
                              (b7, d7) = pick(r6.head, x, b6, d6)
                              r7 = r6.tail
                              match r7:
                                case List/Nil:
                                  return b7
                                case List/Cons:
                                  (b8, d8) = pick(r7.head, x, b7, d7)
                                  r8 = r7.tail
                                  match r8:
                                    case List/Nil:
                                      return b8
                                    case List/Cons:
                                      (b9, d9) = pick(r8.head, x, b8, d8)
                                      r9 = r8.tail
                                      match r9:
                                        case List/Nil:
                                          return b9
                                        case List/Cons:
                                          (b10, d10) = pick(r9.head, x, b9, d9)
                                          r10 = r9.tail
                                          match r10:
                                            case List/Nil:
                                              return b10
                                            case List/Cons:
                                              (b11, d11) = pick(r10.head, x, b10, d10)
                                              r11 = r10.tail
                                              match r11:
                                                case List/Nil:
                                                  return b11
                                                case List/Cons:
                                                  (b12, d12) = pick(r11.head, x, b11, d11)
                                                  r12 = r11.tail
                                                  match r12:
                                                    case List/Nil:
                                                      return b12
                                                    case List/Cons:
                                                      (b13, d13) = pick(r12.head, x, b12, d12)
                                                      r13 = r12.tail
                                                      match r13:
                                                        case List/Nil:
                                                          return b13
                                                        case List/Cons:
                                                          (b14, d14) = pick(r13.head, x, b13, d13)
                                                          r14 = r13.tail
                                                          match r14:
                                                            case List/Nil:
                                                              return b14
                                                            case List/Cons:
                                                              (b15, d15) = pick(r14.head, x, b14, d14)
                                                              r15 = r14.tail
                                                              match r15:
                                                                case List/Nil:
                                                                  return b15
                                                                case List/Cons:
                                                                  (b16, d16) = pick(r15.head, x, b15, d15)
                                                                  return scan16(r15.tail, x, b16, d16)

def pick(candidate, x, best, best_dist):
  d = absdiff(candidate, x)
  if d < best_dist:
    return (candidate, d)
  else:
    if d == best_dist:
      if candidate < best:
        return (candidate, d)
      else:
        return (best, best_dist)
    else:
      return (best, best_dist)

def absdiff(a, b):
  if a >= b:
    return a - b
  else:
    return b - a
