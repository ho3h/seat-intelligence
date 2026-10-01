def prog(x):
  (p, xs) = x
  (lo_rev, hi_rev) = partition(xs, p, [], [])
  return (reverse(lo_rev, []), reverse(hi_rev, []))

def partition(xs, p, lo, hi):
  match xs:
    case List/Nil:
      return (lo, hi)
    case List/Cons:
      if xs.head < p:
        return partition(xs.tail, p, List/Cons(xs.head, lo), hi)
      else:
        return partition(xs.tail, p, lo, List/Cons(xs.head, hi))

def reverse(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse(xs.tail, List/Cons(xs.head, acc))
