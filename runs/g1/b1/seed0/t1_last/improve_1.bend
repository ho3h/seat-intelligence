def prog(xs):
  return last8(xs, 0)

def last8(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      x1 = xs.tail
      match x1:
        case List/Nil:
          return xs.head
        case List/Cons:
          x2 = x1.tail
          match x2:
            case List/Nil:
              return x1.head
            case List/Cons:
              x3 = x2.tail
              match x3:
                case List/Nil:
                  return x2.head
                case List/Cons:
                  x4 = x3.tail
                  match x4:
                    case List/Nil:
                      return x3.head
                    case List/Cons:
                      x5 = x4.tail
                      match x5:
                        case List/Nil:
                          return x4.head
                        case List/Cons:
                          x6 = x5.tail
                          match x6:
                            case List/Nil:
                              return x5.head
                            case List/Cons:
                              x7 = x6.tail
                              match x7:
                                case List/Nil:
                                  return x6.head
                                case List/Cons:
                                  x8 = x7.tail
                                  match x8:
                                    case List/Nil:
                                      return x7.head
                                    case List/Cons:
                                      return last8(x8.tail, x8.head)
