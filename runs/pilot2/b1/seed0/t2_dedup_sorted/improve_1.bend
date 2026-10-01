def prog(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      return dedup_from(xs.head, xs.tail)

def dedup_from(prev, rest):
  match rest:
    case List/Nil:
      return [prev]
    case List/Cons:
      tail = dedup_from(rest.head, rest.tail)
      if prev == rest.head:
        return tail
      else:
        return List/Cons(prev, tail)
