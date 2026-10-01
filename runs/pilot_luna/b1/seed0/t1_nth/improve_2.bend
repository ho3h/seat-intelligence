def prog(x):
  (i, xs) = x
  return nth(i, xs)

def nth(i, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        t1 = xs.tail
        match t1:
          case List/Nil:
            return 0
          case List/Cons:
            if i == 1:
              return t1.head
            else:
              t2 = t1.tail
              match t2:
                case List/Nil:
                  return 0
                case List/Cons:
                  if i == 2:
                    return t2.head
                  else:
                    t3 = t2.tail
                    match t3:
                      case List/Nil:
                        return 0
                      case List/Cons:
                        if i == 3:
                          return t3.head
                        else:
                          t4 = t3.tail
                          match t4:
                            case List/Nil:
                              return 0
                            case List/Cons:
                              if i == 4:
                                return t4.head
                              else:
                                t5 = t4.tail
                                match t5:
                                  case List/Nil:
                                    return 0
                                  case List/Cons:
                                    if i == 5:
                                      return t5.head
                                    else:
                                      t6 = t5.tail
                                      match t6:
                                        case List/Nil:
                                          return 0
                                        case List/Cons:
                                          if i == 6:
                                            return t6.head
                                          else:
                                            t7 = t6.tail
                                            match t7:
                                              case List/Nil:
                                                return 0
                                              case List/Cons:
                                                if i == 7:
                                                  return t7.head
                                                else:
                                                  return nth(i - 8, t7.tail)
