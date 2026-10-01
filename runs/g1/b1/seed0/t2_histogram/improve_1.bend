def prog(xs):
  return histogram(xs, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

def histogram(xs, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15):
  match xs:
    case List/Nil:
      return [c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15]
    case List/Cons:
      if xs.head == 0:
        return histogram(xs.tail, c0 + 1, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15)
      else:
        if xs.head == 1:
          return histogram(xs.tail, c0, c1 + 1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15)
        else:
          if xs.head == 2:
            return histogram(xs.tail, c0, c1, c2 + 1, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15)
          else:
            if xs.head == 3:
              return histogram(xs.tail, c0, c1, c2, c3 + 1, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15)
            else:
              if xs.head == 4:
                return histogram(xs.tail, c0, c1, c2, c3, c4 + 1, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15)
              else:
                if xs.head == 5:
                  return histogram(xs.tail, c0, c1, c2, c3, c4, c5 + 1, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15)
                else:
                  if xs.head == 6:
                    return histogram(xs.tail, c0, c1, c2, c3, c4, c5, c6 + 1, c7, c8, c9, c10, c11, c12, c13, c14, c15)
                  else:
                    if xs.head == 7:
                      return histogram(xs.tail, c0, c1, c2, c3, c4, c5, c6, c7 + 1, c8, c9, c10, c11, c12, c13, c14, c15)
                    else:
                      if xs.head == 8:
                        return histogram(xs.tail, c0, c1, c2, c3, c4, c5, c6, c7, c8 + 1, c9, c10, c11, c12, c13, c14, c15)
                      else:
                        if xs.head == 9:
                          return histogram(xs.tail, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9 + 1, c10, c11, c12, c13, c14, c15)
                        else:
                          if xs.head == 10:
                            return histogram(xs.tail, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 + 1, c11, c12, c13, c14, c15)
                          else:
                            if xs.head == 11:
                              return histogram(xs.tail, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11 + 1, c12, c13, c14, c15)
                            else:
                              if xs.head == 12:
                                return histogram(xs.tail, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12 + 1, c13, c14, c15)
                              else:
                                if xs.head == 13:
                                  return histogram(xs.tail, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13 + 1, c14, c15)
                                else:
                                  if xs.head == 14:
                                    return histogram(xs.tail, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14 + 1, c15)
                                  else:
                                    return histogram(xs.tail, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15 + 1)
