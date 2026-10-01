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
          return (xs.head < value) + (xs.tail.head < value) + count_less(value, xs.tail.tail)
