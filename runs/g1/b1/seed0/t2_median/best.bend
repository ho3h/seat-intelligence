def prog(xs):
  n = length(xs)
  return radix_select(xs, n / 2, 8388608)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def head_or_zero(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return xs.head

def partition_bits(xs, mask, zeros, ones, zero_count):
  match xs:
    case List/Nil:
      return ((zeros, ones), zero_count)
    case List/Cons:
      if (xs.head & mask) == 0:
        return partition_bits(
          xs.tail,
          mask,
          List/Cons(xs.head, zeros),
          ones,
          zero_count + 1
        )
      else:
        return partition_bits(
          xs.tail,
          mask,
          zeros,
          List/Cons(xs.head, ones),
          zero_count
        )

def radix_select(xs, k, mask):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if mask == 0:
        return xs.head
      else:
        (parts, zero_count) = partition_bits(xs, mask, [], [], 0)
        (zeros, ones) = parts
        if k < zero_count:
          return radix_select(zeros, k, mask >> 1)
        else:
          return radix_select(ones, k - zero_count, mask >> 1)
