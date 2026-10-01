def prog(x):
  n = list_length(x)
  return sort_n(x, n)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def sort_n(xs, n):
  if n < 2:
    return xs
  else:
    mid = n / 2
    (left, right) = split_at(xs, mid)
    sorted_left = sort_n(left, mid)
    sorted_right = sort_n(right, n - mid)
    return merge_pairs(sorted_left, sorted_right)

def split_at(xs, n):
  if n == 0:
    return (List/Nil, xs)
  else:
    match xs:
      case List/Nil:
        return (List/Nil, List/Nil)
      case List/Cons:
        (left, right) = split_at(xs.tail, n - 1)
        return (List/Cons(xs.head, left), right)

def merge_pairs(left, right):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          (left_key, left_value) = left.head
          (right_key, right_value) = right.head
          if left_key <= right_key:
            merged_tail = merge_pairs(left.tail, right)
            return List/Cons(left.head, merged_tail)
          else:
            merged_tail = merge_pairs(left, right.tail)
            return List/Cons(right.head, merged_tail)
