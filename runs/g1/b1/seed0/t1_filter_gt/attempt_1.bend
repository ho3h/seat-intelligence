def prog(x):
  (k, xs) = x
  return filt(k, xs)

def filt(k, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      rest = filt(k, xs.tail)
      if xs.head > k:
        return List/Cons(xs.head, rest)
      else:
        return rest
