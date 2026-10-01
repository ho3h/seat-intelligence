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
            (left, right) = split_alt(xs)
            sorted_left = sort_top(left, k)
            sorted_right = sort_top(right, k)
            return merge_top(sorted_left, sorted_right, k)

def split_alt(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      x = xs.head
      match xs.tail:
        case List/Nil:
          return ([x], [])
        case List/Cons:
          y = xs.tail.head
          (left, right) = split_alt(xs.tail.tail)
          return (List/Cons(x, left), List/Cons(y, right))

def merge_top(a, b, k):
  if k == 0:
    return []
  else:
    match a:
      case List/Nil:
        return take_n(b, k)
      case List/Cons:
        match b:
          case List/Nil:
            return take_n(a, k)
          case List/Cons:
            if a.head >= b.head:
              return List/Cons(a.head, merge_top(a.tail, b, k - 1))
            else:
              return List/Cons(b.head, merge_top(a, b.tail, k - 1))

def take_n(xs, n):
  if n == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(xs.head, take_n(xs.tail, n - 1))
