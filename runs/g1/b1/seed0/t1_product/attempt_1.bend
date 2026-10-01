def prog(xs):
  return product(xs, 1)

def product(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return product(xs.tail, acc * xs.head)
