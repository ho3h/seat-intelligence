def prog(x):
  (xs, ys) = x
  return append(xs, ys)

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))
