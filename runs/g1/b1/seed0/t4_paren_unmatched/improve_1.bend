def prog(xs):
  return scan(xs, 0, 0)

def scan(xs, unmatched, depth):
  match xs:
    case List/Nil:
      return (unmatched, depth)
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          if xs.head == 40:
            return (unmatched, depth + 1)
          else:
            if depth > 0:
              return (unmatched, depth - 1)
            else:
              return (unmatched + 1, depth)
        case List/Cons:
          rest = tail.tail
          if xs.head == 40:
            if tail.head == 40:
              return scan(rest, unmatched, depth + 2)
            else:
              return scan(rest, unmatched, depth)
          else:
            if tail.head == 40:
              if depth > 0:
                return scan(rest, unmatched, depth)
              else:
                return scan(rest, unmatched + 1, depth + 1)
            else:
              if depth > 1:
                return scan(rest, unmatched, depth - 2)
              else:
                if depth == 1:
                  return scan(rest, unmatched + 1, 0)
                else:
                  return scan(rest, unmatched + 2, 0)
