def prog(xs):
  return radix_desc(xs, 0)

def radix_desc(xs, bit):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          if all_same(xs.tail, xs.head) == 1:
            return xs
          else:
            if bit == 24:
              return xs
            else:
              mask = 1 << (23 - bit)
              (ones, zeros) = split_bits(xs, mask)
              sorted_ones = radix_desc(ones, bit + 1)
              sorted_zeros = radix_desc(zeros, bit + 1)
              return concat(sorted_ones, sorted_zeros)

def all_same(xs, value):
  match xs:
    case List/Nil:
      return 1
    case List/Cons:
      if xs.head == value:
        return all_same(xs.tail, value)
      else:
        return 0

def split_bits(xs, mask):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (ones, zeros) = split_bits(xs.tail, mask)
      if (xs.head & mask) != 0:
        return (List/Cons(xs.head, ones), zeros)
      else:
        return (ones, List/Cons(xs.head, zeros))

def concat(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, concat(xs.tail, ys))
