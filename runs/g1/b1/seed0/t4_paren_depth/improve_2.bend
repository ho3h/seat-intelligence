def prog(xs):
  return scan8(xs, 0, 0)

def scan8(xs, depth, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      if xs.head == 40:
        d1 = depth + 1
        if d1 > best:
          b1 = d1
        else:
          b1 = best
      else:
        d1 = depth - 1
        b1 = best
      xs1 = xs.tail
      match xs1:
        case List/Nil:
          return b1
        case List/Cons:
          if xs1.head == 40:
            d2 = d1 + 1
            if d2 > b1:
              b2 = d2
            else:
              b2 = b1
          else:
            d2 = d1 - 1
            b2 = b1
          xs2 = xs1.tail
          match xs2:
            case List/Nil:
              return b2
            case List/Cons:
              if xs2.head == 40:
                d3 = d2 + 1
                if d3 > b2:
                  b3 = d3
                else:
                  b3 = b2
              else:
                d3 = d2 - 1
                b3 = b2
              xs3 = xs2.tail
              match xs3:
                case List/Nil:
                  return b3
                case List/Cons:
                  if xs3.head == 40:
                    d4 = d3 + 1
                    if d4 > b3:
                      b4 = d4
                    else:
                      b4 = b3
                  else:
                    d4 = d3 - 1
                    b4 = b3
                  xs4 = xs3.tail
                  match xs4:
                    case List/Nil:
                      return b4
                    case List/Cons:
                      if xs4.head == 40:
                        d5 = d4 + 1
                        if d5 > b4:
                          b5 = d5
                        else:
                          b5 = b4
                      else:
                        d5 = d4 - 1
                        b5 = b4
                      xs5 = xs4.tail
                      match xs5:
                        case List/Nil:
                          return b5
                        case List/Cons:
                          if xs5.head == 40:
                            d6 = d5 + 1
                            if d6 > b5:
                              b6 = d6
                            else:
                              b6 = b5
                          else:
                            d6 = d5 - 1
                            b6 = b5
                          xs6 = xs5.tail
                          match xs6:
                            case List/Nil:
                              return b6
                            case List/Cons:
                              if xs6.head == 40:
                                d7 = d6 + 1
                                if d7 > b6:
                                  b7 = d7
                                else:
                                  b7 = b6
                              else:
                                d7 = d6 - 1
                                b7 = b6
                              xs7 = xs6.tail
                              match xs7:
                                case List/Nil:
                                  return b7
                                case List/Cons:
                                  if xs7.head == 40:
                                    d8 = d7 + 1
                                    if d8 > b7:
                                      b8 = d8
                                    else:
                                      b8 = b7
                                  else:
                                    d8 = d7 - 1
                                    b8 = b7
                                  return scan8(xs7.tail, d8, b8)
