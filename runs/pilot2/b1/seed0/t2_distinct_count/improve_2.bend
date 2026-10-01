def prog(xs):
  return distinct_bits(xs, 0)

def distinct_bits(xs, bit):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if bit == 24:
        return 1
      else:
        (zero, one) = split_bit(xs, bit)
        return distinct_bits(zero, bit + 1) + distinct_bits(one, bit + 1)

def split_bit(xs, bit):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (zero, one) = split_bit(xs.tail, bit)
      if ((xs.head >> bit) & 1) == 0:
        return (List/Cons(xs.head, zero), one)
      else:
        return (zero, List/Cons(xs.head, one))
