def prog(x):
  (k, xs) = x
  return process(xs, k, [])

def process(xs, k, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return process(xs.tail, k, top_insert(xs.head, acc, k))

def top_insert(x, ys, n):
  if n == 0:
    return []
  else:
    match ys:
      case List/Nil:
        return [x]
      case List/Cons:
        if x >= ys.head:
          return List/Cons(x, take_n(ys.tail, n - 1))
        else:
          return List/Cons(ys.head, top_insert(x, ys.tail, n - 1))

def take_n(xs, n):
  if n == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(xs.head, take_n(xs.tail, n - 1))
