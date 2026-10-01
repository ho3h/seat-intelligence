def prog(x):
  (xs, t) = x
  return upper_bound(xs, t, 0)

def upper_bound(xs, t, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head <= t:
        return upper_bound(xs.tail, t, acc + 1)
      else:
        return acc
