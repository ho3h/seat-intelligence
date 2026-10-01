def prog(xs):
  return check_sorted(xs)

def check_sorted(xs):
  match xs:
    case List/Nil:
      return 1
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return 1
        case List/Cons:
          if xs.head > xs.tail.head:
            return 0
          else:
            match xs.tail.tail:
              case List/Nil:
                return 1
              case List/Cons:
                if xs.tail.head > xs.tail.tail.head:
                  return 0
                else:
                  match xs.tail.tail.tail:
                    case List/Nil:
                      return 1
                    case List/Cons:
                      if xs.tail.tail.head > xs.tail.tail.tail.head:
                        return 0
                      else:
                        match xs.tail.tail.tail.tail:
                          case List/Nil:
                            return 1
                          case List/Cons:
                            if xs.tail.tail.tail.head > xs.tail.tail.tail.tail.head:
                              return 0
                            else:
                              match xs.tail.tail.tail.tail.tail:
                                case List/Nil:
                                  return 1
                                case List/Cons:
                                  if xs.tail.tail.tail.tail.head > xs.tail.tail.tail.tail.tail.head:
                                    return 0
                                  else:
                                    match xs.tail.tail.tail.tail.tail.tail:
                                      case List/Nil:
                                        return 1
                                      case List/Cons:
                                        if xs.tail.tail.tail.tail.tail.head > xs.tail.tail.tail.tail.tail.tail.head:
                                          return 0
                                        else:
                                          match xs.tail.tail.tail.tail.tail.tail.tail:
                                            case List/Nil:
                                              return 1
                                            case List/Cons:
                                              if xs.tail.tail.tail.tail.tail.tail.head > xs.tail.tail.tail.tail.tail.tail.tail.head:
                                                return 0
                                              else:
                                                match xs.tail.tail.tail.tail.tail.tail.tail.tail:
                                                  case List/Nil:
                                                    return 1
                                                  case List/Cons:
                                                    if xs.tail.tail.tail.tail.tail.tail.tail.head > xs.tail.tail.tail.tail.tail.tail.tail.tail.head:
                                                      return 0
                                                    else:
                                                      match xs.tail.tail.tail.tail.tail.tail.tail.tail.tail:
                                                        case List/Nil:
                                                          return 1
                                                        case List/Cons:
                                                          if xs.tail.tail.tail.tail.tail.tail.tail.tail.head > xs.tail.tail.tail.tail.tail.tail.tail.tail.tail.head:
                                                            return 0
                                                          else:
                                                            return check_sorted(xs.tail.tail.tail.tail.tail.tail.tail.tail.tail)
