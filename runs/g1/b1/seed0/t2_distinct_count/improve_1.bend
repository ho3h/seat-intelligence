def prog(xs):
  sorted = merge_sort(xs)
  return count_distinct(sorted)

def merge_sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alternating(xs)
          sorted_left = merge_sort(left)
          sorted_right = merge_sort(right)
          return merge_sorted(sorted_left, sorted_right)

def split_alternating(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_alternating(xs.tail)
      return (List/Cons(xs.head, right), left)

def merge_sorted(left, right):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          if left.head <= right.head:
            return List/Cons(left.head, merge_sorted(left.tail, right))
          else:
            return List/Cons(right.head, merge_sorted(left, right.tail))

def count_distinct(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return count_changes(xs.tail, xs.head, 1)

def count_changes(xs, previous, count):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      if xs.head == previous:
        return count_changes(xs.tail, previous, count)
      else:
        return count_changes(xs.tail, xs.head, count + 1)
