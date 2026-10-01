def prog(x):
  (xs, ys) = x
  return dot(xs, ys)

def dot(xs, ys):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      match ys:
        case List/Nil:
          return 0
        case List/Cons:
          p1 = xs.head * ys.head
          x1 = xs.tail
          y1 = ys.tail
          match x1:
            case List/Nil:
              return p1
            case List/Cons:
              match y1:
                case List/Nil:
                  return p1
                case List/Cons:
                  p2 = x1.head * y1.head
                  x2 = x1.tail
                  y2 = y1.tail
                  match x2:
                    case List/Nil:
                      return p1 + p2
                    case List/Cons:
                      match y2:
                        case List/Nil:
                          return p1 + p2
                        case List/Cons:
                          p3 = x2.head * y2.head
                          x3 = x2.tail
                          y3 = y2.tail
                          match x3:
                            case List/Nil:
                              return p1 + p2 + p3
                            case List/Cons:
                              match y3:
                                case List/Nil:
                                  return p1 + p2 + p3
                                case List/Cons:
                                  p4 = x3.head * y3.head
                                  x4 = x3.tail
                                  y4 = y3.tail
                                  match x4:
                                    case List/Nil:
                                      return p1 + p2 + p3 + p4
                                    case List/Cons:
                                      match y4:
                                        case List/Nil:
                                          return p1 + p2 + p3 + p4
                                        case List/Cons:
                                          p5 = x4.head * y4.head
                                          x5 = x4.tail
                                          y5 = y4.tail
                                          match x5:
                                            case List/Nil:
                                              return p1 + p2 + p3 + p4 + p5
                                            case List/Cons:
                                              match y5:
                                                case List/Nil:
                                                  return p1 + p2 + p3 + p4 + p5
                                                case List/Cons:
                                                  p6 = x5.head * y5.head
                                                  x6 = x5.tail
                                                  y6 = y5.tail
                                                  match x6:
                                                    case List/Nil:
                                                      return p1 + p2 + p3 + p4 + p5 + p6
                                                    case List/Cons:
                                                      match y6:
                                                        case List/Nil:
                                                          return p1 + p2 + p3 + p4 + p5 + p6
                                                        case List/Cons:
                                                          p7 = x6.head * y6.head
                                                          x7 = x6.tail
                                                          y7 = y6.tail
                                                          match x7:
                                                            case List/Nil:
                                                              return p1 + p2 + p3 + p4 + p5 + p6 + p7
                                                            case List/Cons:
                                                              match y7:
                                                                case List/Nil:
                                                                  return p1 + p2 + p3 + p4 + p5 + p6 + p7
                                                                case List/Cons:
                                                                  p8 = x7.head * y7.head
                                                                  return p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8 + dot(x7.tail, y7.tail)
