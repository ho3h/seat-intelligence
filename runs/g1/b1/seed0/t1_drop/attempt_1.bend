def prog(x):
  (k, xs) = x
  return drop(k, xs)

def drop(k, xs):
  switch k:
    case 0:
      return xs
    case _:
      match xs:
        case List/Nil:
          return []
        case List/Cons:
          return drop(k - 1, xs.tail)
