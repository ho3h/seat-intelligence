def prog(x):
  (xs, ys) = x
  return merge(xs, ys)

def merge(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return List/Cons(xs.head, xs.tail)
        case List/Cons:
          if xs.head <= ys.head:
            return List/Cons(xs.head, merge(xs.tail, List/Cons(ys.head, ys.tail)))
          else:
            return List/Cons(ys.head, merge(List/Cons(xs.head, xs.tail), ys.tail))
