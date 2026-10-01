def prog(x):
  (xs, t) = x
  return search8(xs, t, 0)

def linear(xs, t, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      if xs.head == t:
        return i
      else:
        if xs.head > t:
          return 16777215
        else:
          return linear(xs.tail, t, i + 1)

def search8(xs, t, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      y1 = xs.tail
      match y1:
        case List/Nil:
          return linear(xs, t, i)
        case List/Cons:
          y2 = y1.tail
          match y2:
            case List/Nil:
              return linear(xs, t, i)
            case List/Cons:
              y3 = y2.tail
              match y3:
                case List/Nil:
                  return linear(xs, t, i)
                case List/Cons:
                  y4 = y3.tail
                  match y4:
                    case List/Nil:
                      return linear(xs, t, i)
                    case List/Cons:
                      y5 = y4.tail
                      match y5:
                        case List/Nil:
                          return linear(xs, t, i)
                        case List/Cons:
                          y6 = y5.tail
                          match y6:
                            case List/Nil:
                              return linear(xs, t, i)
                            case List/Cons:
                              y7 = y6.tail
                              match y7:
                                case List/Nil:
                                  return linear(xs, t, i)
                                case List/Cons:
                                  if y7.head < t:
                                    return search8(y7.tail, t, i + 8)
                                  else:
                                    if xs.head == t:
                                      return i
                                    else:
                                      if xs.head > t:
                                        return 16777215
                                      else:
                                        if y1.head == t:
                                          return i + 1
                                        else:
                                          if y1.head > t:
                                            return 16777215
                                          else:
                                            if y2.head == t:
                                              return i + 2
                                            else:
                                              if y2.head > t:
                                                return 16777215
                                              else:
                                                if y3.head == t:
                                                  return i + 3
                                                else:
                                                  if y3.head > t:
                                                    return 16777215
                                                  else:
                                                    if y4.head == t:
                                                      return i + 4
                                                    else:
                                                      if y4.head > t:
                                                        return 16777215
                                                      else:
                                                        if y5.head == t:
                                                          return i + 5
                                                        else:
                                                          if y5.head > t:
                                                            return 16777215
                                                          else:
                                                            if y6.head == t:
                                                              return i + 6
                                                            else:
                                                              if y6.head > t:
                                                                return 16777215
                                                              else:
                                                                if y7.head == t:
                                                                  return i + 7
                                                                else:
                                                                  return 16777215
