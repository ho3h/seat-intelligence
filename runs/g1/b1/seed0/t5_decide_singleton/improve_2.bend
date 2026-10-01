def prog(x):
  (tau, probs) = x
  match probs:
    case List/Nil:
      return 6
    case List/Cons:
      p0 = probs.head
      r1 = probs.tail
      match r1:
        case List/Nil:
          return 6
        case List/Cons:
          p1 = r1.head
          r2 = r1.tail
          match r2:
            case List/Nil:
              return 6
            case List/Cons:
              p2 = r2.head
              r3 = r2.tail
              match r3:
                case List/Nil:
                  return 6
                case List/Cons:
                  p3 = r3.head
                  r4 = r3.tail
                  match r4:
                    case List/Nil:
                      return 6
                    case List/Cons:
                      p4 = r4.head
                      r5 = r4.tail
                      match r5:
                        case List/Nil:
                          return 6
                        case List/Cons:
                          p5 = r5.head
                          k0 = (p0 << 3) + 5
                          k1 = (p1 << 3) + 4
                          k2 = (p2 << 3) + 3
                          k3 = (p3 << 3) + 2
                          k4 = (p4 << 3) + 1
                          k5 = p5 << 3
                          a = max2(k0, k1)
                          b = max2(k2, k3)
                          c = max2(k4, k5)
                          d = max2(a, b)
                          winner = max2(d, c)
                          if (winner >> 3) >= tau:
                            return 5 - (winner & 7)
                          else:
                            return 6

def max2(a, b):
  if a >= b:
    return a
  else:
    return b
