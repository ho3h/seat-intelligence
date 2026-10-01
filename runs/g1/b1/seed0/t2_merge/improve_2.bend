def prog(x):
  (xs, ys) = x
  return merge(xs, ys)

def merge(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      x0 = xs.head
      x1 = xs.tail
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          y0 = ys.head
          y1 = ys.tail
          if x0 <= y0:
            match x1:
              case List/Nil:
                return List/Cons(x0, ys)
              case List/Cons:
                if x1.head <= y0:
                  x2 = x1.tail
                  match x2:
                    case List/Nil:
                      return List/Cons(x0, List/Cons(x1.head, ys))
                    case List/Cons:
                      if x2.head <= y0:
                        return List/Cons(x0, List/Cons(x1.head, List/Cons(x2.head, merge(x2.tail, ys))))
                      else:
                        return List/Cons(x0, List/Cons(x1.head, List/Cons(y0, merge(x2, y1))))
                else:
                  match y1:
                    case List/Nil:
                      return List/Cons(x0, List/Cons(y0, x1))
                    case List/Cons:
                      if x1.head <= y1.head:
                        return List/Cons(x0, List/Cons(y0, List/Cons(x1.head, merge(x1.tail, y1))))
                      else:
                        return List/Cons(x0, List/Cons(y0, List/Cons(y1.head, merge(x1, y1.tail))))
          else:
            match y1:
              case List/Nil:
                return List/Cons(y0, xs)
              case List/Cons:
                if y1.head < x0:
                  y2 = y1.tail
                  match y2:
                    case List/Nil:
                      return List/Cons(y0, List/Cons(y1.head, xs))
                    case List/Cons:
                      if y2.head < x0:
                        return List/Cons(y0, List/Cons(y1.head, List/Cons(y2.head, merge(xs, y2.tail))))
                      else:
                        return List/Cons(y0, List/Cons(y1.head, List/Cons(x0, merge(x1, y2))))
                else:
                  match x1:
                    case List/Nil:
                      return List/Cons(y0, List/Cons(x0, y1))
                    case List/Cons:
                      if x1.head <= y1.head:
                        return List/Cons(y0, List/Cons(x0, List/Cons(x1.head, merge(x1.tail, y1))))
                      else:
                        return List/Cons(y0, List/Cons(x0, List/Cons(y1.head, merge(x1, y1.tail))))
