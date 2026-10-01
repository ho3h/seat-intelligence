def prog(x):
  (value, xs) = x
  return count_less(value, xs)

def count_less(value, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      match xs.tail:
        case List/Nil:
          if xs.head < value:
            return 1
          else:
            return 0
        case List/Cons:
          pair_count = count_pair(value, xs.head, xs.tail.head)
          rest_count = count_less(value, xs.tail.tail)
          return pair_count + rest_count

def count_pair(value, a, b):
  if a < value:
    if b < value:
      return 2
    else:
      return 1
  else:
    if b < value:
      return 1
    else:
      return 0
