def prog(xs):
  sorted = sort_list(xs)
  return count_unique(sorted)

def sort_list(xs):
  n = list_length(xs)
  if n <= 1:
    return xs
  else:
    (left, right) = split_at(xs, n / 2)
    sorted_left = sort_list(left)
    sorted_right = sort_list(right)
    return merge_sorted(sorted_left, sorted_right)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def split_at(xs, n):
  if n == 0:
    return ([], xs)
  else:
    match xs:
      case List/Nil:
        return ([], [])
      case List/Cons:
        (left, right) = split_at(xs.tail, n - 1)
        return (List/Cons(xs.head, left), right)

def merge_sorted(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if a.head <= b.head:
            rest = merge_sorted(a.tail, b)
            return List/Cons(a.head, rest)
          else:
            rest = merge_sorted(a, b.tail)
            return List/Cons(b.head, rest)

def count_unique(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + count_after(xs.head, xs.tail)

def count_after(previous, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == previous:
        return count_after(previous, xs.tail)
      else:
        return 1 + count_after(xs.head, xs.tail)
