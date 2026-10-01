def prog(xs):
  return scan(xs, 0, 0, 0)

def advance1(c, depth, pos, best):
  if c == 40:
    return ((depth + 1, pos + 1), (best, 1))
  else:
    if depth == 0:
      return ((depth, pos), (best, 0))
    else:
      if depth == 1:
        return ((0, pos + 1), (pos + 1, 1))
      else:
        return ((depth - 1, pos + 1), (best, 1))

def advance2(a, b, depth, pos, best):
  if a == 40:
    if b == 40:
      return ((depth + 2, pos + 2), (best, 1))
    else:
      if depth == 0:
        return ((depth, pos + 2), (pos + 2, 1))
      else:
        return ((depth, pos + 2), (best, 1))
  else:
    if depth == 0:
      return ((depth, pos), (best, 0))
    else:
      if b == 40:
        if depth == 1:
          return ((depth, pos + 2), (pos + 1, 1))
        else:
          return ((depth, pos + 2), (best, 1))
      else:
        if depth == 1:
          return ((0, pos + 1), (pos + 1, 0))
        else:
          if depth == 2:
            return ((0, pos + 2), (pos + 2, 1))
          else:
            return ((depth - 2, pos + 2), (best, 1))

def scan(xs, depth, pos, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      match xs.tail:
        case List/Nil:
          ((d1, p1), (b1, a1)) = advance1(xs.head, depth, pos, best)
          return b1
        case List/Cons:
          ((d1, p1), (b1, a1)) = advance2(xs.head, xs.tail.head, depth, pos, best)
          if a1 == 0:
            return b1
          else:
            rest = xs.tail.tail
            match rest:
              case List/Nil:
                return b1
              case List/Cons:
                match rest.tail:
                  case List/Nil:
                    ((d2, p2), (b2, a2)) = advance1(rest.head, d1, p1, b1)
                    return b2
                  case List/Cons:
                    ((d2, p2), (b2, a2)) = advance2(rest.head, rest.tail.head, d1, p1, b1)
                    if a2 == 0:
                      return b2
                    else:
                      return scan(rest.tail.tail, d2, p2, b2)
