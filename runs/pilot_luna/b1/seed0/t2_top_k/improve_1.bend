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
            (left, right) = split_evenodd(xs)
            sorted_left = sort_top(left, k)
            sorted_right = sort_top(right, k)
            return merge_top(sorted_left, sorted_right, k)

def split_evenodd(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_swap(xs.tail)
      return (List/Cons(xs.head, left), right)

def split_swap(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_evenodd(xs.tail)
      return (List/Cons(xs.head, right), left)

def merge_top(left, right, k):
  if k == 0:
    return []
  else:
    match left:
      case List/Nil:
        return take(k, right)
      case List/Cons:
        match right:
          case List/Nil:
            return take(k, left)
          case List/Cons:
            if left.head >= right.head:
              rest = merge_top(left.tail, right, k - 1)
              return List/Cons(left.head, rest)
            else:
              rest = merge_top(left, right.tail, k - 1)
              return List/Cons(right.head, rest)

def take(k, xs):
  if k == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        rest = take(k - 1, xs.tail)
        return List/Cons(xs.head, rest)
