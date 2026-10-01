def prog(xs):
  return dedup(xs, 0, 0)

def dedup(xs, prev, has_prev):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if has_prev == 1:
        if xs.head == prev:
          return dedup(xs.tail, prev, has_prev)
        else:
          return List/Cons(xs.head, dedup(xs.tail, xs.head, 1))
      else:
        return List/Cons(xs.head, dedup(xs.tail, xs.head, 1))
