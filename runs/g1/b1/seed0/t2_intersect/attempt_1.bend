def prog(x):
  (xs, ys) = x
  return intersect(xs, ys)

def intersect(xs, ys):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match ys:
        case List/Nil:
          return []
        case List/Cons:
          if xs.head == ys.head:
            return List/Cons(xs.head, intersect(xs.tail, ys.tail))
          else:
            if xs.head < ys.head:
              return intersect(xs.tail, ys)
            else:
              return intersect(xs, ys.tail)
