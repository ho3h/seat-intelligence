def prog(xs):
  return dedup(xs, 0, 0)

def dedup(xs, prev, seen):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a = xs.head
      match xs.tail:
        case List/Nil:
          if seen == 1:
            if a == prev:
              return []
            else:
              return [a]
          else:
            return [a]
        case List/Cons:
          b = xs.tail.head
          rest = xs.tail.tail
          tail = dedup(rest, b, 1)
          if seen == 1:
            keep_a = a != prev
          else:
            keep_a = 1
          keep_b = b != a
          if keep_a == 1:
            if keep_b == 1:
              return List/Cons(a, List/Cons(b, tail))
            else:
              return List/Cons(a, tail)
          else:
            if keep_b == 1:
              return List/Cons(b, tail)
            else:
              return tail
