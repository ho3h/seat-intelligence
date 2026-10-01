def prog(xs):
  (sorted, inversions) = sort_count(xs)
  return inversions

def sort_count(xs):
  n = list_length(xs)
  if n < 2:
    return (xs, 0)
  else:
    mid = n / 2
    (left, right) = split_at(xs, mid)
    (sorted_left, count_left) = sort_count(left)
    (sorted_right, count_right) = sort_count(right)
    (merged, cross_count) = merge_count(sorted_left, mid, sorted_right)
    return (merged, count_left + count_right + cross_count)

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

def merge_count(left, left_len, right):
  match left:
    case List/Nil:
      return (right, 0)
    case List/Cons:
      match right:
        case List/Nil:
          return (left, 0)
        case List/Cons:
          if left.head <= right.head:
            (merged_tail, count) = merge_count(left.tail, left_len - 1, right)
            return (List/Cons(left.head, merged_tail), count)
          else:
            (merged_tail, count) = merge_count(left, left_len, right.tail)
            return (List/Cons(right.head, merged_tail), count + left_len)
