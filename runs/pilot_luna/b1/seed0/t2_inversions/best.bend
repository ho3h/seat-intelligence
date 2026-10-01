def prog(xs):
  return inversions(xs, 0)

def inversions(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      count = count_smaller(xs.tail, xs.head, 0)
      return inversions(xs.tail, acc + count)

def count_smaller(xs, value, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head < value:
        return count_smaller(xs.tail, value, acc + 1)
      else:
        return count_smaller(xs.tail, value, acc)
