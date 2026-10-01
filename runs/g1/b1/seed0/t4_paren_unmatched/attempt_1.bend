def prog(xs):
  return scan(xs, 0, 0)

def scan(xs, unmatched, depth):
  match xs:
    case List/Nil:
      return (unmatched, depth)
    case List/Cons:
      if xs.head == 40:
        return scan(xs.tail, unmatched, depth + 1)
      else:
        if depth > 0:
          return scan(xs.tail, unmatched, depth - 1)
        else:
          return scan(xs.tail, unmatched + 1, depth)
