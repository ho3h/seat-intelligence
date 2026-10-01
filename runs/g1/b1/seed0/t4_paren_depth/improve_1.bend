def prog(xs):
  return scan4(xs, 0, 0)

def scan4(xs, depth, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      if xs.head == 40:
        d1 = depth + 1
        if d1 > best:
          b1 = d1
        else:
          b1 = best
      else:
        d1 = depth - 1
        b1 = best
      ys = xs.tail
      match ys:
        case List/Nil:
          return b1
        case List/Cons:
          if ys.head == 40:
            d2 = d1 + 1
            if d2 > b1:
              b2 = d2
            else:
              b2 = b1
          else:
            d2 = d1 - 1
            b2 = b1
          zs = ys.tail
          match zs:
            case List/Nil:
              return b2
            case List/Cons:
              if zs.head == 40:
                d3 = d2 + 1
                if d3 > b2:
                  b3 = d3
                else:
                  b3 = b2
              else:
                d3 = d2 - 1
                b3 = b2
              ws = zs.tail
              match ws:
                case List/Nil:
                  return b3
                case List/Cons:
                  if ws.head == 40:
                    d4 = d3 + 1
                    if d4 > b3:
                      b4 = d4
                    else:
                      b4 = b3
                  else:
                    d4 = d3 - 1
                    b4 = b3
                  return scan4(ws.tail, d4, b4)
