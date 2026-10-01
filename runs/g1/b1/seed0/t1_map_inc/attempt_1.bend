def prog(xs):
  return map_inc(xs)

def map_inc(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      return List/Cons(xs.head + 1, map_inc(xs.tail))
