def prog(x):
  (k, xs) = x
  if k == 0:
    return []
  else:
    return process(xs, [], k)

def process(xs, acc, k):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      next = insert_top(xs.head, acc, k)
      return process(xs.tail, next, k)

def insert_top(x, ys, k):
  if k == 0:
    return []
  else:
    match ys:
      case List/Nil:
        return [x]
      case List/Cons:
        if x > ys.head:
          return List/Cons(x, take_n(ys, k - 1))
        else:
          rest = insert_top(x, ys.tail, k - 1)
          return List/Cons(ys.head, rest)

def take_n(xs, n):
  if n == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        rest = take_n(xs.tail, n - 1)
        return List/Cons(xs.head, rest)
