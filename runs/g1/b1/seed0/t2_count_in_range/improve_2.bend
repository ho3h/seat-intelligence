def prog(x):
  (lo, hi, xs) = x
  return count_in_range(lo, hi, xs, 0)

def count_in_range(lo, hi, xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      a0 = xs.head
      acc1 = acc + ((a0 >= lo) & (a0 <= hi))
      r1 = xs.tail
      match r1:
        case List/Nil:
          return acc1
        case List/Cons:
          a1 = r1.head
          acc2 = acc1 + ((a1 >= lo) & (a1 <= hi))
          r2 = r1.tail
          match r2:
            case List/Nil:
              return acc2
            case List/Cons:
              a2 = r2.head
              acc3 = acc2 + ((a2 >= lo) & (a2 <= hi))
              r3 = r2.tail
              match r3:
                case List/Nil:
                  return acc3
                case List/Cons:
                  a3 = r3.head
                  acc4 = acc3 + ((a3 >= lo) & (a3 <= hi))
                  r4 = r3.tail
                  match r4:
                    case List/Nil:
                      return acc4
                    case List/Cons:
                      a4 = r4.head
                      acc5 = acc4 + ((a4 >= lo) & (a4 <= hi))
                      r5 = r4.tail
                      match r5:
                        case List/Nil:
                          return acc5
                        case List/Cons:
                          a5 = r5.head
                          acc6 = acc5 + ((a5 >= lo) & (a5 <= hi))
                          r6 = r5.tail
                          match r6:
                            case List/Nil:
                              return acc6
                            case List/Cons:
                              a6 = r6.head
                              acc7 = acc6 + ((a6 >= lo) & (a6 <= hi))
                              r7 = r6.tail
                              match r7:
                                case List/Nil:
                                  return acc7
                                case List/Cons:
                                  a7 = r7.head
                                  acc8 = acc7 + ((a7 >= lo) & (a7 <= hi))
                                  r8 = r7.tail
                                  match r8:
                                    case List/Nil:
                                      return acc8
                                    case List/Cons:
                                      a8 = r8.head
                                      acc9 = acc8 + ((a8 >= lo) & (a8 <= hi))
                                      r9 = r8.tail
                                      match r9:
                                        case List/Nil:
                                          return acc9
                                        case List/Cons:
                                          a9 = r9.head
                                          acc10 = acc9 + ((a9 >= lo) & (a9 <= hi))
                                          r10 = r9.tail
                                          match r10:
                                            case List/Nil:
                                              return acc10
                                            case List/Cons:
                                              a10 = r10.head
                                              acc11 = acc10 + ((a10 >= lo) & (a10 <= hi))
                                              r11 = r10.tail
                                              match r11:
                                                case List/Nil:
                                                  return acc11
                                                case List/Cons:
                                                  a11 = r11.head
                                                  acc12 = acc11 + ((a11 >= lo) & (a11 <= hi))
                                                  r12 = r11.tail
                                                  match r12:
                                                    case List/Nil:
                                                      return acc12
                                                    case List/Cons:
                                                      a12 = r12.head
                                                      acc13 = acc12 + ((a12 >= lo) & (a12 <= hi))
                                                      r13 = r12.tail
                                                      match r13:
                                                        case List/Nil:
                                                          return acc13
                                                        case List/Cons:
                                                          a13 = r13.head
                                                          acc14 = acc13 + ((a13 >= lo) & (a13 <= hi))
                                                          r14 = r13.tail
                                                          match r14:
                                                            case List/Nil:
                                                              return acc14
                                                            case List/Cons:
                                                              a14 = r14.head
                                                              acc15 = acc14 + ((a14 >= lo) & (a14 <= hi))
                                                              r15 = r14.tail
                                                              match r15:
                                                                case List/Nil:
                                                                  return acc15
                                                                case List/Cons:
                                                                  a15 = r15.head
                                                                  acc16 = acc15 + ((a15 >= lo) & (a15 <= hi))
                                                                  return count_in_range(lo, hi, r15.tail, acc16)
