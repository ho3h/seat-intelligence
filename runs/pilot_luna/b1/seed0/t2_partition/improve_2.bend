def prog(x):
  (p, xs) = x
  return partition(xs, p)

def partition(xs, p):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          if xs.head < p:
            return ([xs.head], [])
          else:
            return ([], [xs.head])
        case List/Cons:
          (lo, hi) = partition(xs.tail.tail, p)
          if xs.tail.head < p:
            lo = List/Cons(xs.tail.head, lo)
          else:
            hi = List/Cons(xs.tail.head, hi)
          if xs.head < p:
            lo = List/Cons(xs.head, lo)
          else:
            hi = List/Cons(xs.head, hi)
          return (lo, hi)
