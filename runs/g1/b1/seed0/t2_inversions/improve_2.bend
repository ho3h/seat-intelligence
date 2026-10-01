def prog(xs):
  return bit_inversions(xs, 23)

def bit_inversions(xs, bit):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return 0
        case List/Cons:
          (zeros, ones, cross) = partition_bit(xs, bit, 0)
          if bit == 0:
            return cross
          else:
            lower_zeros = bit_inversions(zeros, bit - 1)
            lower_ones = bit_inversions(ones, bit - 1)
            return cross + lower_zeros + lower_ones

def partition_bit(xs, bit, seen_ones):
  match xs:
    case List/Nil:
      return ([], [], 0)
    case List/Cons:
      if ((xs.head >> bit) & 1) == 0:
        (zeros, ones, cross) = partition_bit(xs.tail, bit, seen_ones)
        return (List/Cons(xs.head, zeros), ones, cross + seen_ones)
      else:
        (zeros, ones, cross) = partition_bit(xs.tail, bit, seen_ones + 1)
        return (zeros, List/Cons(xs.head, ones), cross)
