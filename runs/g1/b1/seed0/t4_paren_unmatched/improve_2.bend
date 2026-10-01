def prog(xs):
  return scan4(xs, 0, 0)

def step(ch, unmatched, depth):
  if ch == 40:
    return (unmatched, depth + 1)
  else:
    if depth > 0:
      return (unmatched, depth - 1)
    else:
      return (unmatched + 1, depth)

def scan(xs, unmatched, depth):
  match xs:
    case List/Nil:
      return (unmatched, depth)
    case List/Cons:
      (u1, d1) = step(xs.head, unmatched, depth)
      return scan(xs.tail, u1, d1)

def scan4(xs, unmatched, depth):
  match xs:
    case List/Nil:
      return (unmatched, depth)
    case List/Cons:
      (u1, d1) = step(xs.head, unmatched, depth)
      match xs.tail:
        case List/Nil:
          return (u1, d1)
        case List/Cons:
          (u2, d2) = step(xs.tail.head, u1, d1)
          match xs.tail.tail:
            case List/Nil:
              return (u2, d2)
            case List/Cons:
              (u3, d3) = step(xs.tail.tail.head, u2, d2)
              match xs.tail.tail.tail:
                case List/Nil:
                  return (u3, d3)
                case List/Cons:
                  (u4, d4) = step(xs.tail.tail.tail.head, u3, d3)
                  return scan4(xs.tail.tail.tail.tail, u4, d4)
