def prog(xs):
  return go(xs, 0, 0)

def go(xs, m1, m2):
  match xs:
    case List/Nil:
      return m2
    case List/Cons:
      x = xs.head
      if x >= m1:
        return go(xs.tail, x, m1)
      else:
        if x > m2:
          return go(xs.tail, m1, x)
        else:
          return go(xs.tail, m1, m2)
