def prog(xs):
  sorted = sort_list(xs)
  match sorted:
    case List/Nil:
      return 0
    case List/Cons:
      (count, rest) = count_run(sorted.tail, sorted.head, 1)
      return scan_runs(rest, sorted.head, count, sorted.head, count)

def sort_list(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alternating(xs)
          return merge_sorted(sort_list(left), sort_list(right))

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

def count_run(xs, value, count):
  match xs:
    case List/Nil:
      return (count, [])
    case List/Cons:
      if xs.head == value:
        return count_run(xs.tail, value, count + 1)
      else:
        return (count, xs)

def scan_runs(xs, current_value, current_count, best_value, best_count):
  match xs:
    case List/Nil:
      return best_value
    case List/Cons:
      (count, rest) = count_run(xs.tail, xs.head, 1)
      if count > best_count:
        return scan_runs(rest, xs.head, count, xs.head, count)
      else:
        return scan_runs(rest, xs.head, count, best_value, best_count)
