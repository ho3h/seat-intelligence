def prog(x):
  (k, xs) = x
  (count, low, high) = list_stats(xs)
  if k >= count:
    return 0
  else:
    if low == high:
      return low
    else:
      return radix_select(xs, k, 24, 0, low, high)

def list_stats(xs):
  match xs:
    case List/Nil:
      return (0, 0, 0)
    case List/Cons:
      return list_stats_acc(xs.tail, 1, xs.head, xs.head)

def list_stats_acc(xs, count, low, high):
  match xs:
    case List/Nil:
      return (count, low, high)
    case List/Cons:
      if xs.head < low:
        next_low = xs.head
      else:
        next_low = low
      if xs.head > high:
        next_high = xs.head
      else:
        next_high = high
      return list_stats_acc(xs.tail, count + 1, next_low, next_high)

def radix_select(xs, k, bit, prefix, low, high):
  if bit == 0:
    return prefix
  else:
    mask = 1 << (bit - 1)
    low_bit = (low >> (bit - 1)) & 1
    high_bit = (high >> (bit - 1)) & 1
    if low_bit == high_bit:
      if low_bit == 0:
        return radix_select(xs, k, bit - 1, prefix, low, high)
      else:
        return radix_select(xs, k, bit - 1, prefix | mask, low, high)
    else:
      (zeros, zero_count, ones, one_count) = partition_bit(xs, mask, List/Nil, 0, List/Nil, 0)
      if k < zero_count:
        return radix_select(zeros, k, bit - 1, prefix, low, high)
      else:
        return radix_select(ones, k - zero_count, bit - 1, prefix | mask, low, high)

def partition_bit(xs, mask, zeros, zero_count, ones, one_count):
  match xs:
    case List/Nil:
      return (zeros, zero_count, ones, one_count)
    case List/Cons:
      if (xs.head & mask) == 0:
        return partition_bit(xs.tail, mask, List/Cons(xs.head, zeros), zero_count + 1, ones, one_count)
      else:
        return partition_bit(xs.tail, mask, zeros, zero_count, List/Cons(xs.head, ones), one_count + 1)
