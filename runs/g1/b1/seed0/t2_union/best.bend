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
          if xs.head < ys.head:
            return List/Cons(xs.head, merge_y(xs.tail, ys.head, ys.tail))
          else:
            if xs.head == ys.head:
              return List/Cons(xs.head, merge(xs.tail, ys.tail))
            else:
              return List/Cons(ys.head, merge_x(xs.head, xs.tail, ys.tail))

def merge_y(xs, yh, yt):
  match xs:
    case List/Nil:
      return List/Cons(yh, yt)
    case List/Cons:
      if xs.head < yh:
        return List/Cons(xs.head, merge_y(xs.tail, yh, yt))
      else:
        if xs.head == yh:
          return List/Cons(xs.head, merge(xs.tail, yt))
        else:
          return List/Cons(yh, merge_x(xs.head, xs.tail, yt))

def merge_x(xh, xt, ys):
  match ys:
    case List/Nil:
      return List/Cons(xh, xt)
    case List/Cons:
      if xh < ys.head:
        return List/Cons(xh, merge_y(xt, ys.head, ys.tail))
      else:
        if xh == ys.head:
          return List/Cons(xh, merge(xt, ys.tail))
        else:
          return List/Cons(ys.head, merge_x(xh, xt, ys.tail))
