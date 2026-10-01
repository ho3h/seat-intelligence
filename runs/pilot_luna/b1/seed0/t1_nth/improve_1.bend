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
        tail = xs.tail
        match tail:
          case List/Nil:
            return 0
          case List/Cons:
            if i == 1:
              return tail.head
            else:
              return nth(i - 2, tail.tail)
