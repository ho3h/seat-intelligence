def prog(xs):
  return count_even(xs, 0)

def count_even(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      acc1 = acc + (1 - (xs.head & 1))
      ys = xs.tail
      match ys:
        case List/Nil:
          return acc1
        case List/Cons:
          acc2 = acc1 + (1 - (ys.head & 1))
          zs = ys.tail
          match zs:
            case List/Nil:
              return acc2
            case List/Cons:
              acc3 = acc2 + (1 - (zs.head & 1))
              ws = zs.tail
              match ws:
                case List/Nil:
                  return acc3
                case List/Cons:
                  acc4 = acc3 + (1 - (ws.head & 1))
                  vs = ws.tail
                  match vs:
                    case List/Nil:
                      return acc4
                    case List/Cons:
                      acc5 = acc4 + (1 - (vs.head & 1))
                      us = vs.tail
                      match us:
                        case List/Nil:
                          return acc5
                        case List/Cons:
                          acc6 = acc5 + (1 - (us.head & 1))
                          ts = us.tail
                          match ts:
                            case List/Nil:
                              return acc6
                            case List/Cons:
                              acc7 = acc6 + (1 - (ts.head & 1))
                              rs = ts.tail
                              match rs:
                                case List/Nil:
                                  return acc7
                                case List/Cons:
                                  acc8 = acc7 + (1 - (rs.head & 1))
                                  return count_even(rs.tail, acc8)
