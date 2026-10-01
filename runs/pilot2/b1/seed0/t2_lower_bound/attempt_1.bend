def prog(x):
  (xs, t) = x
  return lower(xs, t, 0)

def lower(xs, t, count):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      if xs.head < t:
        return lower(xs.tail, t, count + 1)
      else:
        return count
