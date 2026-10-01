def prog(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      return List/Cons(xs.head, dedup_pairs(xs.tail, xs.head))

def dedup_pairs(xs, prev):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a = xs.head
      match xs.tail:
        case List/Nil:
          if a == prev:
            return []
          else:
            return List/Cons(a, [])
        case List/Cons:
          b = xs.tail.head
          rest = dedup_pairs(xs.tail.tail, b)
          if a == prev:
            if b == a:
              return rest
            else:
              return List/Cons(b, rest)
          else:
            if b == a:
              return List/Cons(a, rest)
            else:
              return List/Cons(a, List/Cons(b, rest))
