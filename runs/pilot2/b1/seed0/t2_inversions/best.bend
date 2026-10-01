def prog(xs):
  n = list_length(xs)
  (sorted, count, length) = sort_count(xs, n)
  return count

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def split_at(xs, k):
  if k == 0:
    return ([], xs)
  else:
    match xs:
      case List/Nil:
        return ([], [])
      case List/Cons:
        (front, back) = split_at(xs.tail, k - 1)
        return (List/Cons(xs.head, front), back)

def sort_count(xs, n):
  if n < 2:
    return (xs, 0, n)
  else:
    k = n / 2
    (left, right) = split_at(xs, k)
    (sorted_left, count_left, length_left) = sort_count(left, k)
    (sorted_right, count_right, length_right) = sort_count(right, n - k)
    (merged, cross_count) = merge_count(sorted_left, sorted_right, length_left)
    return (merged, count_left + count_right + cross_count, n)

def merge_count(left, right, length_left):
  match left:
    case List/Nil:
      return (right, 0)
    case List/Cons:
      match right:
        case List/Nil:
          return (left, 0)
        case List/Cons:
          if left.head <= right.head:
            (tail, count) = merge_count(left.tail, right, length_left - 1)
            return (List/Cons(left.head, tail), count)
          else:
            (tail, count) = merge_count(left, right.tail, length_left)
            return (List/Cons(right.head, tail), count + length_left)
