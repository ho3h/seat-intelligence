def prog(xs):
  return count_even(xs, 0)

def count_even(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      acc1 = acc + (1 - (xs.head & 1))
      a = xs.tail
      match a:
        case List/Nil:
          return acc1
        case List/Cons:
          acc2 = acc1 + (1 - (a.head & 1))
          b = a.tail
          match b:
            case List/Nil:
              return acc2
            case List/Cons:
              acc3 = acc2 + (1 - (b.head & 1))
              c = b.tail
              match c:
                case List/Nil:
                  return acc3
                case List/Cons:
                  acc4 = acc3 + (1 - (c.head & 1))
                  d = c.tail
                  match d:
                    case List/Nil:
                      return acc4
                    case List/Cons:
                      acc5 = acc4 + (1 - (d.head & 1))
                      e = d.tail
                      match e:
                        case List/Nil:
                          return acc5
                        case List/Cons:
                          acc6 = acc5 + (1 - (e.head & 1))
                          f = e.tail
                          match f:
                            case List/Nil:
                              return acc6
                            case List/Cons:
                              acc7 = acc6 + (1 - (f.head & 1))
                              g = f.tail
                              match g:
                                case List/Nil:
                                  return acc7
                                case List/Cons:
                                  acc8 = acc7 + (1 - (g.head & 1))
                                  h = g.tail
                                  match h:
                                    case List/Nil:
                                      return acc8
                                    case List/Cons:
                                      acc9 = acc8 + (1 - (h.head & 1))
                                      i = h.tail
                                      match i:
                                        case List/Nil:
                                          return acc9
                                        case List/Cons:
                                          acc10 = acc9 + (1 - (i.head & 1))
                                          j = i.tail
                                          match j:
                                            case List/Nil:
                                              return acc10
                                            case List/Cons:
                                              acc11 = acc10 + (1 - (j.head & 1))
                                              k = j.tail
                                              match k:
                                                case List/Nil:
                                                  return acc11
                                                case List/Cons:
                                                  acc12 = acc11 + (1 - (k.head & 1))
                                                  l = k.tail
                                                  match l:
                                                    case List/Nil:
                                                      return acc12
                                                    case List/Cons:
                                                      acc13 = acc12 + (1 - (l.head & 1))
                                                      m = l.tail
                                                      match m:
                                                        case List/Nil:
                                                          return acc13
                                                        case List/Cons:
                                                          acc14 = acc13 + (1 - (m.head & 1))
                                                          n = m.tail
                                                          match n:
                                                            case List/Nil:
                                                              return acc14
                                                            case List/Cons:
                                                              acc15 = acc14 + (1 - (n.head & 1))
                                                              o = n.tail
                                                              match o:
                                                                case List/Nil:
                                                                  return acc15
                                                                case List/Cons:
                                                                  acc16 = acc15 + (1 - (o.head & 1))
                                                                  p = o.tail
                                                                  match p:
                                                                    case List/Nil:
                                                                      return acc16
                                                                    case List/Cons:
                                                                      acc17 = acc16 + (1 - (p.head & 1))
                                                                      return count_even(p.tail, acc17)
