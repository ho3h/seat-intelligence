def prog(x):
  (xs, t) = x
  return lower8(xs, t, 0)

def lower8(xs, t, count):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      if xs.head < t:
        ys = xs.tail
        match ys:
          case List/Nil:
            return count + 1
          case List/Cons:
            if ys.head < t:
              zs = ys.tail
              match zs:
                case List/Nil:
                  return count + 2
                case List/Cons:
                  if zs.head < t:
                    ws = zs.tail
                    match ws:
                      case List/Nil:
                        return count + 3
                      case List/Cons:
                        if ws.head < t:
                          vs = ws.tail
                          match vs:
                            case List/Nil:
                              return count + 4
                            case List/Cons:
                              if vs.head < t:
                                us = vs.tail
                                match us:
                                  case List/Nil:
                                    return count + 5
                                  case List/Cons:
                                    if us.head < t:
                                      rs = us.tail
                                      match rs:
                                        case List/Nil:
                                          return count + 6
                                        case List/Cons:
                                          if rs.head < t:
                                            qs = rs.tail
                                            match qs:
                                              case List/Nil:
                                                return count + 7
                                              case List/Cons:
                                                if qs.head < t:
                                                  return lower8(qs.tail, t, count + 8)
                                                else:
                                                  return count + 7
                                          else:
                                            return count + 6
                                    else:
                                      return count + 5
                              else:
                                return count + 4
                        else:
                          return count + 3
                  else:
                    return count + 2
            else:
              return count + 1
      else:
        return count
