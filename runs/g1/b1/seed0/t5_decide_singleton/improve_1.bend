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
                          a = choose((0, p0), (1, p1))
                          b = choose((2, p2), (3, p3))
                          c = choose((4, p4), (5, p5))
                          d = choose(a, b)
                          winner = choose(d, c)
                          (index, value) = winner
                          if value >= tau:
                            return index
                          else:
                            return 6

def choose(a, b):
  (index_a, value_a) = a
  (index_b, value_b) = b
  if value_a >= value_b:
    return a
  else:
    return b
