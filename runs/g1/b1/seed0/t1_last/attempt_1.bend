def prog(xs):
  return last(xs, 0)

def last(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return last(xs.tail, xs.head)
