def prog(x):
  (k, cands) = x
  return sort_top(k, cands)

def comes_first(a, b):
  (u1, v1, s1) = a
  (u2, v2, s2) = b
  if s1 > s2:
    return 1
  else:
    if s1 < s2:
      return 0
    else:
      if u1 < u2:
        return 1
      else:
        if u1 > u2:
          return 0
        else:
          if v1 < v2:
            return 1
          else:
            return 0

def split_half(xs):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return (List/Cons(xs.head, List/Nil), List/Nil)
        case List/Cons:
          (left, right) = split_half(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def sort_top(k, xs):
  if k == 0:
    return List/Nil
  else:
    match xs:
      case List/Nil:
        return List/Nil
      case List/Cons:
        match xs.tail:
          case List/Nil:
            return xs
          case List/Cons:
            (left, right) = split_half(xs)
            sorted_left = sort_top(k, left)
            sorted_right = sort_top(k, right)
            return merge_top(k, sorted_left, sorted_right)

def merge_top(k, a, b):
  if k == 0:
    return List/Nil
  else:
    match a:
      case List/Nil:
        return take_k(k, b)
      case List/Cons:
        match b:
          case List/Nil:
            return take_k(k, a)
          case List/Cons:
            if comes_first(a.head, b.head) == 1:
              return List/Cons(a.head, merge_top(k - 1, a.tail, b))
            else:
              return List/Cons(b.head, merge_top(k - 1, a, b.tail))

def take_k(k, xs):
  if k == 0:
    return List/Nil
  else:
    match xs:
      case List/Nil:
        return List/Nil
      case List/Cons:
        return List/Cons(xs.head, take_k(k - 1, xs.tail))
