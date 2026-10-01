def prog(xs):
  return count_inversions(xs)

def count_inversions(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      smaller = count_smaller(xs.head, xs.tail)
      return smaller + count_inversions(xs.tail)

def count_smaller(value, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head < value:
        return 1 + count_smaller(value, xs.tail)
      else:
        return count_smaller(value, xs.tail)
