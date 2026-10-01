def prog(x):
  (lo, hi, xs) = x
  return count_in_range(lo, hi, xs, 0)

def count_in_range(lo, hi, xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head >= lo:
        if xs.head <= hi:
          return count_in_range(lo, hi, xs.tail, acc + 1)
        else:
          return count_in_range(lo, hi, xs.tail, acc)
      else:
        return count_in_range(lo, hi, xs.tail, acc)
