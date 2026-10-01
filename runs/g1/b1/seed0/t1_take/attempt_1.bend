def prog(x):
  (k, xs) = x
  return take(k, xs)

def take(k, xs):
  if k == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(xs.head, take(k - 1, xs.tail))
