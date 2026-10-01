def prog(x):
  (xs, t) = x
  return lower_bound(xs, t, 0)

def lower_bound(xs, t, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head < t:
        return lower_bound(xs.tail, t, acc + 1)
      else:
        return acc
