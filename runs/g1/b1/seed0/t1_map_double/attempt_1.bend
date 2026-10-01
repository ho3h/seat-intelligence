def prog(xs):
  return map_double(xs)

def map_double(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      return List/Cons(xs.head * 2, map_double(xs.tail))
