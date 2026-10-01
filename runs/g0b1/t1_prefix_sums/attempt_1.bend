def prog(xs):
  return go(xs, 0)

def go(xs, acc):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      s = acc + xs.head
      return List/Cons(s, go(xs.tail, s))
