def prog(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      return List/Cons(xs.head, dedup_tail(xs.tail, xs.head))

def dedup_tail(xs, prev):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == prev:
        return dedup_tail(xs.tail, prev)
      else:
        return List/Cons(xs.head, dedup_tail(xs.tail, xs.head))
