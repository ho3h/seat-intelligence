def prog(xs):
  return last32(xs, 0)

def last32(xs, acc):
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
                                      x9 = x8.tail
                                      match x9:
                                        case List/Nil:
                                          return x8.head
                                        case List/Cons:
                                          x10 = x9.tail
                                          match x10:
                                            case List/Nil:
                                              return x9.head
                                            case List/Cons:
                                              x11 = x10.tail
                                              match x11:
                                                case List/Nil:
                                                  return x10.head
                                                case List/Cons:
                                                  x12 = x11.tail
                                                  match x12:
                                                    case List/Nil:
                                                      return x11.head
                                                    case List/Cons:
                                                      x13 = x12.tail
                                                      match x13:
                                                        case List/Nil:
                                                          return x12.head
                                                        case List/Cons:
                                                          x14 = x13.tail
                                                          match x14:
                                                            case List/Nil:
                                                              return x13.head
                                                            case List/Cons:
                                                              x15 = x14.tail
                                                              match x15:
                                                                case List/Nil:
                                                                  return x14.head
                                                                case List/Cons:
                                                                  x16 = x15.tail
                                                                  match x16:
                                                                    case List/Nil:
                                                                      return x15.head
                                                                    case List/Cons:
                                                                      x17 = x16.tail
                                                                      match x17:
                                                                        case List/Nil:
                                                                          return x16.head
                                                                        case List/Cons:
                                                                          x18 = x17.tail
                                                                          match x18:
                                                                            case List/Nil:
                                                                              return x17.head
                                                                            case List/Cons:
                                                                              x19 = x18.tail
                                                                              match x19:
                                                                                case List/Nil:
                                                                                  return x18.head
                                                                                case List/Cons:
                                                                                  x20 = x19.tail
                                                                                  match x20:
                                                                                    case List/Nil:
                                                                                      return x19.head
                                                                                    case List/Cons:
                                                                                      x21 = x20.tail
                                                                                      match x21:
                                                                                        case List/Nil:
                                                                                          return x20.head
                                                                                        case List/Cons:
                                                                                          x22 = x21.tail
                                                                                          match x22:
                                                                                            case List/Nil:
                                                                                              return x21.head
                                                                                            case List/Cons:
                                                                                              x23 = x22.tail
                                                                                              match x23:
                                                                                                case List/Nil:
                                                                                                  return x22.head
                                                                                                case List/Cons:
                                                                                                  x24 = x23.tail
                                                                                                  match x24:
                                                                                                    case List/Nil:
                                                                                                      return x23.head
                                                                                                    case List/Cons:
                                                                                                      x25 = x24.tail
                                                                                                      match x25:
                                                                                                        case List/Nil:
                                                                                                          return x24.head
                                                                                                        case List/Cons:
                                                                                                          x26 = x25.tail
                                                                                                          match x26:
                                                                                                            case List/Nil:
                                                                                                              return x25.head
                                                                                                            case List/Cons:
                                                                                                              x27 = x26.tail
                                                                                                              match x27:
                                                                                                                case List/Nil:
                                                                                                                  return x26.head
                                                                                                                case List/Cons:
                                                                                                                  x28 = x27.tail
                                                                                                                  match x28:
                                                                                                                    case List/Nil:
                                                                                                                      return x27.head
                                                                                                                    case List/Cons:
                                                                                                                      x29 = x28.tail
                                                                                                                      match x29:
                                                                                                                        case List/Nil:
                                                                                                                          return x28.head
                                                                                                                        case List/Cons:
                                                                                                                          x30 = x29.tail
                                                                                                                          match x30:
                                                                                                                            case List/Nil:
                                                                                                                              return x29.head
                                                                                                                            case List/Cons:
                                                                                                                              x31 = x30.tail
                                                                                                                              match x31:
                                                                                                                                case List/Nil:
                                                                                                                                  return x30.head
                                                                                                                                case List/Cons:
                                                                                                                                  return last32(x31.tail, x31.head)
