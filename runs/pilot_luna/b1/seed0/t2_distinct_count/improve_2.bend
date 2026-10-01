def prog(xs):
  return radix_count(xs, 0)

def radix_count(xs, bit):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if bit == 24:
        return 1
      else:
        (zeros, ones) = partition(xs, bit, [], [])
        return radix_count(zeros, bit + 1) + radix_count(ones, bit + 1)

def partition(xs, bit, zeros, ones):
  match xs:
    case List/Nil:
      return (zeros, ones)
    case List/Cons:
      if ((xs.head >> bit) & 1) == 0:
        return partition(xs.tail, bit, List/Cons(xs.head, zeros), ones)
      else:
        return partition(xs.tail, bit, zeros, List/Cons(xs.head, ones))
