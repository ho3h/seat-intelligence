def prog(p):
  return roots(p)

def roots(p):
  (q, stable) = jump(p, p)
  if stable == 1:
    return q
  else:
    return roots(q)

def jump(full, xs):
  match xs:
    case List/Nil:
      return ([], 1)
    case List/Cons:
      target = get(full, xs.head)
      (tail, stable) = jump(full, xs.tail)
      if target == xs.head:
        return (List/Cons(target, tail), stable)
      else:
        return (List/Cons(target, tail), 0)

def get(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get(xs.tail, i - 1)
