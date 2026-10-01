def prog(p):
  return roots(p)

def roots(p):
  (out, done) = double(p, p, 0)
  if done == 1:
    return out
  else:
    return roots(out)

def double(full, xs, i):
  match xs:
    case List/Nil:
      return ([], 1)
    case List/Cons:
      target = get(full, xs.head)
      (tail, done) = double(full, xs.tail, i + 1)
      if target == i:
        return (List/Cons(target, tail), done)
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
