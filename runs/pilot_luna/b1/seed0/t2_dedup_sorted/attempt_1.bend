def prog(xs):
  return dedup(xs, 0, 0)

def dedup(xs, has_prev, prev):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if has_prev == 1:
        if xs.head == prev:
          return dedup(xs.tail, 1, prev)
        else:
          return List/Cons(xs.head, dedup(xs.tail, 1, xs.head))
      else:
        return List/Cons(xs.head, dedup(xs.tail, 1, xs.head))
