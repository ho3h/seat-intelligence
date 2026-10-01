def prog(xs):
  return max_list(xs)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

def max_list(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          return xs.head
        case List/Cons:
          pair_max = max2(xs.head, tail.head)
          rest_max = max_list(tail.tail)
          return max2(pair_max, rest_max)
