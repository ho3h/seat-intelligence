def prog(x):
  (k, xs) = x
  return sort_top(xs, k)

def sort_top(xs, k):
  if k == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        match xs.tail:
          case List/Nil:
            return [xs.head]
          case List/Cons:
            (left, right) = split_pairs(xs)
            sorted_left = sort_top(left, k)
            sorted_right = sort_top(right, k)
            return merge_top(sorted_left, sorted_right, k)

def split_pairs(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return ([xs.head], [])
        case List/Cons:
          (left, right) = split_pairs(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def merge_top(left, right, k):
  if k == 0:
    return []
  else:
    match left:
      case List/Nil:
        return take_n(right, k)
      case List/Cons:
        match right:
          case List/Nil:
            return take_n(left, k)
          case List/Cons:
            if left.head >= right.head:
              rest = merge_top(left.tail, right, k - 1)
              return List/Cons(left.head, rest)
            else:
              rest = merge_top(left, right.tail, k - 1)
              return List/Cons(right.head, rest)

def take_n(xs, n):
  if n == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        rest = take_n(xs.tail, n - 1)
        return List/Cons(xs.head, rest)
