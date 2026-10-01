def prog(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      return List/Cons(xs.head, dd(xs.head, xs.tail))

def dd(prev, xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if xs.head == prev:
        return dd(prev, xs.tail)
      else:
        return List/Cons(xs.head, dd(xs.head, xs.tail))
