def prog(x):
  (value, xs) = x
  return count_less(value, xs, 0)

def count_less(value, xs, count):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      if xs.head < value:
        return count_less(value, xs.tail, count + 1)
      else:
        return count_less(value, xs.tail, count)
