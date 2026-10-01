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
      first = xs.head
      rest = xs.tail
      match rest:
        case List/Nil:
          if first == prev:
            return []
          else:
            return List/Cons(first, [])
        case List/Cons:
          second = rest.head
          tail = rest.tail
          if first == prev:
            if second == first:
              return dedup_pairs(tail, second)
            else:
              return List/Cons(second, dedup_pairs(tail, second))
          else:
            if second == first:
              return List/Cons(first, dedup_pairs(tail, first))
            else:
              return List/Cons(first, List/Cons(second, dedup_pairs(tail, second)))
