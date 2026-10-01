def prog(x):
  (xs, t) = x
  return lower(xs, t, 0)

def lower(xs, t, count):
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
                          return lower(ws.tail, t, count + 4)
                        else:
                          return count + 3
                  else:
                    return count + 2
            else:
              return count + 1
      else:
        return count
