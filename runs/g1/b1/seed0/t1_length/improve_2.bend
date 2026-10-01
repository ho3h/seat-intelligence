def prog(xs):
  return length(xs)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      a = xs.tail
      match a:
        case List/Nil:
          return 1
        case List/Cons:
          b = a.tail
          match b:
            case List/Nil:
              return 2
            case List/Cons:
              c = b.tail
              match c:
                case List/Nil:
                  return 3
                case List/Cons:
                  d = c.tail
                  match d:
                    case List/Nil:
                      return 4
                    case List/Cons:
                      e = d.tail
                      match e:
                        case List/Nil:
                          return 5
                        case List/Cons:
                          f = e.tail
                          match f:
                            case List/Nil:
                              return 6
                            case List/Cons:
                              g = f.tail
                              match g:
                                case List/Nil:
                                  return 7
                                case List/Cons:
                                  h = g.tail
                                  match h:
                                    case List/Nil:
                                      return 8
                                    case List/Cons:
                                      i = h.tail
                                      match i:
                                        case List/Nil:
                                          return 9
                                        case List/Cons:
                                          j = i.tail
                                          match j:
                                            case List/Nil:
                                              return 10
                                            case List/Cons:
                                              k = j.tail
                                              match k:
                                                case List/Nil:
                                                  return 11
                                                case List/Cons:
                                                  l = k.tail
                                                  match l:
                                                    case List/Nil:
                                                      return 12
                                                    case List/Cons:
                                                      m = l.tail
                                                      match m:
                                                        case List/Nil:
                                                          return 13
                                                        case List/Cons:
                                                          n = m.tail
                                                          match n:
                                                            case List/Nil:
                                                              return 14
                                                            case List/Cons:
                                                              o = n.tail
                                                              match o:
                                                                case List/Nil:
                                                                  return 15
                                                                case List/Cons:
                                                                  p = o.tail
                                                                  match p:
                                                                    case List/Nil:
                                                                      return 16
                                                                    case List/Cons:
                                                                      q = p.tail
                                                                      match q:
                                                                        case List/Nil:
                                                                          return 17
                                                                        case List/Cons:
                                                                          r = q.tail
                                                                          match r:
                                                                            case List/Nil:
                                                                              return 18
                                                                            case List/Cons:
                                                                              s = r.tail
                                                                              match s:
                                                                                case List/Nil:
                                                                                  return 19
                                                                                case List/Cons:
                                                                                  t = s.tail
                                                                                  match t:
                                                                                    case List/Nil:
                                                                                      return 20
                                                                                    case List/Cons:
                                                                                      u = t.tail
                                                                                      match u:
                                                                                        case List/Nil:
                                                                                          return 21
                                                                                        case List/Cons:
                                                                                          v = u.tail
                                                                                          match v:
                                                                                            case List/Nil:
                                                                                              return 22
                                                                                            case List/Cons:
                                                                                              w = v.tail
                                                                                              match w:
                                                                                                case List/Nil:
                                                                                                  return 23
                                                                                                case List/Cons:
                                                                                                  x = w.tail
                                                                                                  match x:
                                                                                                    case List/Nil:
                                                                                                      return 24
                                                                                                    case List/Cons:
                                                                                                      y = x.tail
                                                                                                      match y:
                                                                                                        case List/Nil:
                                                                                                          return 25
                                                                                                        case List/Cons:
                                                                                                          z = y.tail
                                                                                                          match z:
                                                                                                            case List/Nil:
                                                                                                              return 26
                                                                                                            case List/Cons:
                                                                                                              aa = z.tail
                                                                                                              match aa:
                                                                                                                case List/Nil:
                                                                                                                  return 27
                                                                                                                case List/Cons:
                                                                                                                  ab = aa.tail
                                                                                                                  match ab:
                                                                                                                    case List/Nil:
                                                                                                                      return 28
                                                                                                                    case List/Cons:
                                                                                                                      ac = ab.tail
                                                                                                                      match ac:
                                                                                                                        case List/Nil:
                                                                                                                          return 29
                                                                                                                        case List/Cons:
                                                                                                                          ad = ac.tail
                                                                                                                          match ad:
                                                                                                                            case List/Nil:
                                                                                                                              return 30
                                                                                                                            case List/Cons:
                                                                                                                              ae = ad.tail
                                                                                                                              match ae:
                                                                                                                                case List/Nil:
                                                                                                                                  return 31
                                                                                                                                case List/Cons:
                                                                                                                                  af = ae.tail
                                                                                                                                  match af:
                                                                                                                                    case List/Nil:
                                                                                                                                      return 32
                                                                                                                                    case List/Cons:
                                                                                                                                      return 32 + length(af.tail)
