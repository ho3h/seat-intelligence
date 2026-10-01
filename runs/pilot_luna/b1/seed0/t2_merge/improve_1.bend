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
          return xs
        case List/Cons:
          if xs.head <= ys.head:
            return drain_x(xs, ys.head, ys)
          else:
            return drain_y(ys, xs.head, xs)

def drain_x(xs, pivot, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      if xs.head <= pivot:
        return List/Cons(xs.head, drain_x(xs.tail, pivot, ys))
      else:
        return merge(xs, ys)

def drain_y(ys, pivot, xs):
  match ys:
    case List/Nil:
      return xs
    case List/Cons:
      if ys.head <= pivot:
        return List/Cons(ys.head, drain_y(ys.tail, pivot, xs))
      else:
        return merge(xs, ys)
