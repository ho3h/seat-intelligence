def prog(x):
  (p, xs) = x
  return partition(xs, p)

def partition(xs, p):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (lo, hi) = partition(xs.tail, p)
      if xs.head < p:
        return (List/Cons(xs.head, lo), hi)
      else:
        return (lo, List/Cons(xs.head, hi))
