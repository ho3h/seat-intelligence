def prog(xs):
  (values0, values1, values2, values3) = collect(xs, [], [], [], [])
  return [
    trie_count(values0, 23),
    trie_count(values1, 23),
    trie_count(values2, 23),
    trie_count(values3, 23)
  ]

def collect(xs, values0, values1, values2, values3):
  match xs:
    case List/Nil:
      return (values0, values1, values2, values3)
    case List/Cons:
      (node, key, value) = xs.head
      if key == 0:
        return collect(xs.tail, List/Cons(value, values0), values1, values2, values3)
      else:
        if key == 1:
          return collect(xs.tail, values0, List/Cons(value, values1), values2, values3)
        else:
          if key == 2:
            return collect(xs.tail, values0, values1, List/Cons(value, values2), values3)
          else:
            return collect(xs.tail, values0, values1, values2, List/Cons(value, values3))

def trie_count(xs, bit):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      switch bit:
        case 0:
          (zeros, ones) = partition_bit(xs, bit)
          return nonempty(zeros) + nonempty(ones)
        case _:
          (zeros, ones) = partition_bit(xs, bit)
          return trie_count(zeros, bit - 1) + trie_count(ones, bit - 1)

def partition_bit(xs, bit):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (zeros, ones) = partition_bit(xs.tail, bit)
      if ((xs.head >> bit) & 1) == 0:
        return (List/Cons(xs.head, zeros), ones)
      else:
        return (zeros, List/Cons(xs.head, ones))

def nonempty(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1
