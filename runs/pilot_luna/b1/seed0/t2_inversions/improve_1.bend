def prog(xs):
  (sorted, count, size) = sort_count(xs)
  return count

def split_pairs(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      rest = xs.tail
      match rest:
        case List/Nil:
          return ([xs.head], [])
        case List/Cons:
          (left, right) = split_pairs(rest.tail)
          return (List/Cons(xs.head, left), List/Cons(rest.head, right))

def sort_count(xs):
  match xs:
    case List/Nil:
      return ([], 0, 0)
    case List/Cons:
      rest = xs.tail
      match rest:
        case List/Nil:
          return (xs, 0, 1)
        case List/Cons:
          (left, right) = split_pairs(xs)
          (sorted_left, inv_left, len_left) = sort_count(left)
          (sorted_right, inv_right, len_right) = sort_count(right)
          (sorted, cross) = merge_count(sorted_left, sorted_right, len_left)
          return (sorted, inv_left + inv_right + cross, len_left + len_right)

def merge_count(left, right, left_len):
  match left:
    case List/Nil:
      return (right, 0)
    case List/Cons:
      match right:
        case List/Nil:
          return (left, 0)
        case List/Cons:
          if left.head <= right.head:
            (tail, count) = merge_count(left.tail, right, left_len - 1)
            return (List/Cons(left.head, tail), count)
          else:
            (tail, count) = merge_count(left, right.tail, left_len)
            return (List/Cons(right.head, tail), count + left_len)
