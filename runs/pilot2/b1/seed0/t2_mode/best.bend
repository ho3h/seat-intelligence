def prog(xs):
  ordered = sort_values(xs)
  match ordered:
    case List/Nil:
      return 0
    case List/Cons:
      return scan_mode(ordered.tail, ordered.head, 1, ordered.head, 1)

def sort_values(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_pairs(xs)
          sorted_left = sort_values(left)
          sorted_right = sort_values(right)
          return merge_sorted(sorted_left, sorted_right)

def split_pairs(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      first = xs.head
      match xs.tail:
        case List/Nil:
          return ([first], [])
        case List/Cons:
          second = xs.tail.head
          (left, right) = split_pairs(xs.tail.tail)
          return (List/Cons(first, left), List/Cons(second, right))

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

def scan_mode(xs, current, current_count, best, best_count):
  match xs:
    case List/Nil:
      if current_count > best_count:
        return current
      else:
        return best
    case List/Cons:
      if xs.head == current:
        return scan_mode(xs.tail, current, current_count + 1, best, best_count)
      else:
        if current_count > best_count:
          return scan_mode(xs.tail, xs.head, 1, current, current_count)
        else:
          return scan_mode(xs.tail, xs.head, 1, best, best_count)
