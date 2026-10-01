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
            return List/Cons(xs.head, merge_x(xs.tail, ys.head, ys.tail))
          else:
            return List/Cons(ys.head, merge_y(xs.head, xs.tail, ys.tail))

def merge_x(xs, y, yt):
  match xs:
    case List/Nil:
      return List/Cons(y, yt)
    case List/Cons:
      if xs.head <= y:
        return List/Cons(xs.head, merge_x(xs.tail, y, yt))
      else:
        return List/Cons(y, merge(xs, yt))

def merge_y(x, xt, ys):
  match ys:
    case List/Nil:
      return List/Cons(x, xt)
    case List/Cons:
      if x <= ys.head:
        return List/Cons(x, merge(xt, ys))
      else:
        return List/Cons(ys.head, merge_y(x, xt, ys.tail))
