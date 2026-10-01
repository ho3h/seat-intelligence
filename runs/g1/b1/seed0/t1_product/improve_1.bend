def prog(xs):
  return product(xs, 1)

def product(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      next = acc * xs.head
      if next == 0:
        return 0
      else:
        return product(xs.tail, next)
