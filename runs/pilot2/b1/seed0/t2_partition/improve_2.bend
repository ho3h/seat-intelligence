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
          first_lo = xs.head < p
          second_lo = xs.tail.head < p
          (lo, hi) = partition(xs.tail.tail, p)
          if first_lo:
            if second_lo:
              return (List/Cons(xs.head, List/Cons(xs.tail.head, lo)), hi)
            else:
              return (List/Cons(xs.head, lo), List/Cons(xs.tail.head, hi))
          else:
            if second_lo:
              return (List/Cons(xs.tail.head, lo), List/Cons(xs.head, hi))
            else:
              return (lo, List/Cons(xs.head, List/Cons(xs.tail.head, hi)))
