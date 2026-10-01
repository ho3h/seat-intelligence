def prog(x):
  (k, xs) = x
  return radix_top(xs, k, 24, [])

def radix_top(xs, k, depth, suffix):
  if k == 0:
    return suffix
  else:
    match xs:
      case List/Nil:
        return suffix
      case List/Cons:
        switch depth:
          case 0:
            return take_append(k, xs, suffix)
          case _:
            bit = depth - 1
            (ones, zeros, ones_count) = partition_bit(xs, bit)
            if k <= ones_count:
              return radix_top(ones, k, bit, suffix)
            else:
              low = radix_top(zeros, k - ones_count, bit, suffix)
              return radix_top(ones, ones_count, bit, low)

def partition_bit(xs, bit):
  match xs:
    case List/Nil:
      return ([], [], 0)
    case List/Cons:
      (ones, zeros, count) = partition_bit(xs.tail, bit)
      if ((xs.head >> bit) & 1) == 1:
        return (List/Cons(xs.head, ones), zeros, count + 1)
      else:
        return (ones, List/Cons(xs.head, zeros), count)

def take_append(k, xs, suffix):
  if k == 0:
    return suffix
  else:
    match xs:
      case List/Nil:
        return suffix
      case List/Cons:
        return List/Cons(xs.head, take_append(k - 1, xs.tail, suffix))
