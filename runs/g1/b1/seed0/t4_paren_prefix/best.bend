def prog(xs):
  return scan(xs, 0, 0, 0)

def scan(xs, depth, pos, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      match xs.tail:
        case List/Nil:
          if xs.head == 40:
            return best
          else:
            if depth == 0:
              return best
            else:
              if depth == 1:
                return pos + 1
              else:
                return best
        case List/Cons:
          if xs.head == 40:
            if xs.tail.head == 40:
              return scan(xs.tail.tail, depth + 2, pos + 2, best)
            else:
              if depth == 0:
                return scan(xs.tail.tail, depth, pos + 2, pos + 2)
              else:
                return scan(xs.tail.tail, depth, pos + 2, best)
          else:
            if depth == 0:
              return best
            else:
              if xs.tail.head == 40:
                if depth == 1:
                  return scan(xs.tail.tail, depth, pos + 2, pos + 1)
                else:
                  return scan(xs.tail.tail, depth, pos + 2, best)
              else:
                if depth == 1:
                  return pos + 1
                else:
                  if depth == 2:
                    return scan(xs.tail.tail, 0, pos + 2, pos + 2)
                  else:
                    return scan(xs.tail.tail, depth - 2, pos + 2, best)
