def prog(x):
  (xs, t) = x
  return lb(xs, t, 0)

def lb(xs, t, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head < t:
        return lb(xs.tail, t, acc + 1)
      else:
        return acc
