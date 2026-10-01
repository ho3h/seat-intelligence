def prog(xs):
  return scan(xs, 0, 0)

def scan(xs, depth, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      if xs.head == 40:
        d = depth + 1
        if d > best:
          return scan(xs.tail, d, d)
        else:
          return scan(xs.tail, d, best)
      else:
        return scan(xs.tail, depth - 1, best)
