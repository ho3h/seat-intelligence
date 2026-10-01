def prog(x):
  (xs, ys) = x
  return zip_add(xs, ys)

def zip_add(xs, ys):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match ys:
        case List/Nil:
          return []
        case List/Cons:
          tail = zip_add(xs.tail, ys.tail)
          return List/Cons(xs.head + ys.head, tail)
