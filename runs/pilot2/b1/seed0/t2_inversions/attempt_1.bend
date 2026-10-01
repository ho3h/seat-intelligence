def prog(xs):
  return inversions(xs)

def inversions(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return count_smaller(xs.tail, xs.head) + inversions(xs.tail)

def count_smaller(xs, x):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head < x:
        return 1 + count_smaller(xs.tail, x)
      else:
        return count_smaller(xs.tail, x)
