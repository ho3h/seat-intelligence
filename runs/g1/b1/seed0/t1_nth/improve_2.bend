def prog(x):
  (i, xs) = x
  return nth(i, xs)

def nth(i, xs):
  if i < 32:
    return nth_small(i, xs)
  else:
    rest = skip32(xs)
    return nth(i - 32, rest)

def nth_small(i, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return nth_small(i - 1, xs.tail)

def skip32(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a1 = xs.tail
      match a1:
        case List/Nil:
          return []
        case List/Cons:
          a2 = a1.tail
          match a2:
            case List/Nil:
              return []
            case List/Cons:
              a3 = a2.tail
              match a3:
                case List/Nil:
                  return []
                case List/Cons:
                  a4 = a3.tail
                  match a4:
                    case List/Nil:
                      return []
                    case List/Cons:
                      a5 = a4.tail
                      match a5:
                        case List/Nil:
                          return []
                        case List/Cons:
                          a6 = a5.tail
                          match a6:
                            case List/Nil:
                              return []
                            case List/Cons:
                              a7 = a6.tail
                              match a7:
                                case List/Nil:
                                  return []
                                case List/Cons:
                                  a8 = a7.tail
                                  match a8:
                                    case List/Nil:
                                      return []
                                    case List/Cons:
                                      a9 = a8.tail
                                      match a9:
                                        case List/Nil:
                                          return []
                                        case List/Cons:
                                          a10 = a9.tail
                                          match a10:
                                            case List/Nil:
                                              return []
                                            case List/Cons:
                                              a11 = a10.tail
                                              match a11:
                                                case List/Nil:
                                                  return []
                                                case List/Cons:
                                                  a12 = a11.tail
                                                  match a12:
                                                    case List/Nil:
                                                      return []
                                                    case List/Cons:
                                                      a13 = a12.tail
                                                      match a13:
                                                        case List/Nil:
                                                          return []
                                                        case List/Cons:
                                                          a14 = a13.tail
                                                          match a14:
                                                            case List/Nil:
                                                              return []
                                                            case List/Cons:
                                                              a15 = a14.tail
                                                              match a15:
                                                                case List/Nil:
                                                                  return []
                                                                case List/Cons:
                                                                  a16 = a15.tail
                                                                  match a16:
                                                                    case List/Nil:
                                                                      return []
                                                                    case List/Cons:
                                                                      a17 = a16.tail
                                                                      match a17:
                                                                        case List/Nil:
                                                                          return []
                                                                        case List/Cons:
                                                                          a18 = a17.tail
                                                                          match a18:
                                                                            case List/Nil:
                                                                              return []
                                                                            case List/Cons:
                                                                              a19 = a18.tail
                                                                              match a19:
                                                                                case List/Nil:
                                                                                  return []
                                                                                case List/Cons:
                                                                                  a20 = a19.tail
                                                                                  match a20:
                                                                                    case List/Nil:
                                                                                      return []
                                                                                    case List/Cons:
                                                                                      a21 = a20.tail
                                                                                      match a21:
                                                                                        case List/Nil:
                                                                                          return []
                                                                                        case List/Cons:
                                                                                          a22 = a21.tail
                                                                                          match a22:
                                                                                            case List/Nil:
                                                                                              return []
                                                                                            case List/Cons:
                                                                                              a23 = a22.tail
                                                                                              match a23:
                                                                                                case List/Nil:
                                                                                                  return []
                                                                                                case List/Cons:
                                                                                                  a24 = a23.tail
                                                                                                  match a24:
                                                                                                    case List/Nil:
                                                                                                      return []
                                                                                                    case List/Cons:
                                                                                                      a25 = a24.tail
                                                                                                      match a25:
                                                                                                        case List/Nil:
                                                                                                          return []
                                                                                                        case List/Cons:
                                                                                                          a26 = a25.tail
                                                                                                          match a26:
                                                                                                            case List/Nil:
                                                                                                              return []
                                                                                                            case List/Cons:
                                                                                                              a27 = a26.tail
                                                                                                              match a27:
                                                                                                                case List/Nil:
                                                                                                                  return []
                                                                                                                case List/Cons:
                                                                                                                  a28 = a27.tail
                                                                                                                  match a28:
                                                                                                                    case List/Nil:
                                                                                                                      return []
                                                                                                                    case List/Cons:
                                                                                                                      a29 = a28.tail
                                                                                                                      match a29:
                                                                                                                        case List/Nil:
                                                                                                                          return []
                                                                                                                        case List/Cons:
                                                                                                                          a30 = a29.tail
                                                                                                                          match a30:
                                                                                                                            case List/Nil:
                                                                                                                              return []
                                                                                                                            case List/Cons:
                                                                                                                              a31 = a30.tail
                                                                                                                              match a31:
                                                                                                                                case List/Nil:
                                                                                                                                  return []
                                                                                                                                case List/Cons:
                                                                                                                                  return a31.tail
