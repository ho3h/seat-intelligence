def prog(x):
  (xs, ys) = x
  return dot(xs, ys, 0)

def dot(xs, ys, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      match ys:
        case List/Nil:
          return acc
        case List/Cons:
          return dot(xs.tail, ys.tail, acc + xs.head * ys.head)
