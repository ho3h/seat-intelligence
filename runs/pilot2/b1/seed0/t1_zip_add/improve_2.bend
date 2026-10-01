def prog(x):
  (xs, ys) = x
  return zip_add(xs, ys)

def zip_add(xs, ys):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match ys:
        case List/Nil:
          return []
        case List/Cons:
          a0 = xs.head + ys.head
          x1 = xs.tail
          y1 = ys.tail
          match x1:
            case List/Nil:
              return List/Cons(a0, [])
            case List/Cons:
              match y1:
                case List/Nil:
                  return List/Cons(a0, [])
                case List/Cons:
                  a1 = x1.head + y1.head
                  x2 = x1.tail
                  y2 = y1.tail
                  match x2:
                    case List/Nil:
                      return List/Cons(a0, List/Cons(a1, []))
                    case List/Cons:
                      match y2:
                        case List/Nil:
                          return List/Cons(a0, List/Cons(a1, []))
                        case List/Cons:
                          a2 = x2.head + y2.head
                          x3 = x2.tail
                          y3 = y2.tail
                          match x3:
                            case List/Nil:
                              return List/Cons(a0, List/Cons(a1, List/Cons(a2, [])))
                            case List/Cons:
                              match y3:
                                case List/Nil:
                                  return List/Cons(a0, List/Cons(a1, List/Cons(a2, [])))
                                case List/Cons:
                                  a3 = x3.head + y3.head
                                  x4 = x3.tail
                                  y4 = y3.tail
                                  match x4:
                                    case List/Nil:
                                      return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, []))))
                                    case List/Cons:
                                      match y4:
                                        case List/Nil:
                                          return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, []))))
                                        case List/Cons:
                                          a4 = x4.head + y4.head
                                          x5 = x4.tail
                                          y5 = y4.tail
                                          match x5:
                                            case List/Nil:
                                              return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, [])))))
                                            case List/Cons:
                                              match y5:
                                                case List/Nil:
                                                  return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, [])))))
                                                case List/Cons:
                                                  a5 = x5.head + y5.head
                                                  x6 = x5.tail
                                                  y6 = y5.tail
                                                  match x6:
                                                    case List/Nil:
                                                      return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, []))))))
                                                    case List/Cons:
                                                      match y6:
                                                        case List/Nil:
                                                          return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, []))))))
                                                        case List/Cons:
                                                          a6 = x6.head + y6.head
                                                          x7 = x6.tail
                                                          y7 = y6.tail
                                                          match x7:
                                                            case List/Nil:
                                                              return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, List/Cons(a6, [])))))))
                                                            case List/Cons:
                                                              match y7:
                                                                case List/Nil:
                                                                  return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, List/Cons(a6, [])))))))
                                                                case List/Cons:
                                                                  a7 = x7.head + y7.head
                                                                  return List/Cons(a0, List/Cons(a1, List/Cons(a2, List/Cons(a3, List/Cons(a4, List/Cons(a5, List/Cons(a6, List/Cons(a7, zip_add(x7.tail, y7.tail)))))))))
