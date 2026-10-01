def prog(x):
  (p, xs) = x
  (lo, hi) = partition(xs, p, [], [])
  return (reverse(lo), reverse(hi))

def partition(xs, p, lo, hi):
  match xs:
    case List/Nil:
      return (lo, hi)
    case List/Cons:
      if xs.head < p:
        return partition(xs.tail, p, List/Cons(xs.head, lo), hi)
      else:
        return partition(xs.tail, p, lo, List/Cons(xs.head, hi))

def reverse(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))
