def prog(x):
  (i, xs) = x
  return nth(i, xs)

def nth(i, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return nth(i - 1, xs.tail)
