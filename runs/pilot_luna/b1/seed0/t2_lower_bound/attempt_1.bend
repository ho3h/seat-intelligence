def prog(x):
  (xs, t) = x
  return count_less(xs, t, 0)

def count_less(xs, t, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head < t:
        return count_less(xs.tail, t, acc + 1)
      else:
        return acc
