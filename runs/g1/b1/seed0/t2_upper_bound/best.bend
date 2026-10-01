def prog(x):
  (xs, t) = x
  return upper_bound(xs, t, 0)

def upper_bound(xs, t, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head <= t:
        ys = xs.tail
        match ys:
          case List/Nil:
            return acc + 1
          case List/Cons:
            if ys.head <= t:
              zs = ys.tail
              match zs:
                case List/Nil:
                  return acc + 2
                case List/Cons:
                  if zs.head <= t:
                    ws = zs.tail
                    match ws:
                      case List/Nil:
                        return acc + 3
                      case List/Cons:
                        if ws.head <= t:
                          return upper_bound(ws.tail, t, acc + 4)
                        else:
                          return acc + 3
                  else:
                    return acc + 2
            else:
              return acc + 1
      else:
        return acc
