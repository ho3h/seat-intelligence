def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return go(xs.tail, 1, xs.head, 0)

def go(xs, i, best, bi):
  match xs:
    case List/Nil:
      return bi
    case List/Cons:
      if xs.head > best:
        return go(xs.tail, i + 1, xs.head, i)
      else:
        return go(xs.tail, i + 1, best, bi)
