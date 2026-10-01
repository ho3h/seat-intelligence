def prog(xs):
  return scan(xs, 0, 0, 0)

def scan(xs, depth, pos, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      if xs.head == 40:
        return scan(xs.tail, depth + 1, pos + 1, best)
      else:
        if depth == 0:
          return best
        else:
          if depth == 1:
            return scan(xs.tail, 0, pos + 1, pos + 1)
          else:
            return scan(xs.tail, depth - 1, pos + 1, best)
