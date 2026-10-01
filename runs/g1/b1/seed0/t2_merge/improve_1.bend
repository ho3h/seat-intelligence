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
            match xs.tail:
              case List/Nil:
                return List/Cons(xs.head, ys)
              case List/Cons:
                if xs.tail.head <= ys.head:
                  return List/Cons(xs.head, List/Cons(xs.tail.head, merge(xs.tail.tail, ys)))
                else:
                  return List/Cons(xs.head, List/Cons(ys.head, merge(xs.tail, ys.tail)))
          else:
            match ys.tail:
              case List/Nil:
                return List/Cons(ys.head, xs)
              case List/Cons:
                if ys.tail.head < xs.head:
                  return List/Cons(ys.head, List/Cons(ys.tail.head, merge(xs, ys.tail.tail)))
                else:
                  return List/Cons(ys.head, List/Cons(xs.head, merge(xs.tail, ys.tail)))
