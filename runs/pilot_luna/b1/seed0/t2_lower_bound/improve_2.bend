def prog(x):
  (xs, t) = x
  return scan8(xs, t, 0)

def scan8(xs, t, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head < t:
        a = xs.tail
        match a:
          case List/Nil:
            return acc + 1
          case List/Cons:
            if a.head < t:
              b = a.tail
              match b:
                case List/Nil:
                  return acc + 2
                case List/Cons:
                  if b.head < t:
                    c = b.tail
                    match c:
                      case List/Nil:
                        return acc + 3
                      case List/Cons:
                        if c.head < t:
                          d = c.tail
                          match d:
                            case List/Nil:
                              return acc + 4
                            case List/Cons:
                              if d.head < t:
                                e = d.tail
                                match e:
                                  case List/Nil:
                                    return acc + 5
                                  case List/Cons:
                                    if e.head < t:
                                      f = e.tail
                                      match f:
                                        case List/Nil:
                                          return acc + 6
                                        case List/Cons:
                                          if f.head < t:
                                            g = f.tail
                                            match g:
                                              case List/Nil:
                                                return acc + 7
                                              case List/Cons:
                                                if g.head < t:
                                                  return scan8(g.tail, t, acc + 8)
                                                else:
                                                  return acc + 7
                                          else:
                                            return acc + 6
                                    else:
                                      return acc + 5
                          else:
                            return acc + 4
                    else:
                      return acc + 3
              else:
                return acc + 2
        else:
          return acc + 1
      else:
        return acc
