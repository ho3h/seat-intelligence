def prog(x):
  (k, xs) = x
  return process(xs, k, [])

def process(xs, k, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      next = insert_keep(xs.head, acc, k)
      return process(xs.tail, k, next)

def insert_keep(x, ys, k):
  if k == 0:
    return []
  else:
    match ys:
      case List/Nil:
        return [x]
      case List/Cons:
        if x >= ys.head:
          rest = take(k - 1, ys)
          return List/Cons(x, rest)
        else:
          rest = insert_keep(x, ys.tail, k - 1)
          return List/Cons(ys.head, rest)

def take(k, xs):
  if k == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        rest = take(k - 1, xs.tail)
        return List/Cons(xs.head, rest)
