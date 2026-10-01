def prog(xs):
  sorted = sort(xs)
  match sorted:
    case List/Nil:
      return 0
    case List/Cons:
      return find_mode(sorted.tail, sorted.head, 1, sorted.head, 0)

def sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split(xs, [], [], 0)
          sorted_left = sort(left)
          sorted_right = sort(right)
          return merge(sorted_left, sorted_right)

def split(xs, left, right, turn):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if turn == 0:
        return split(xs.tail, List/Cons(xs.head, left), right, 1)
      else:
        return split(xs.tail, left, List/Cons(xs.head, right), 0)

def merge(left, right):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          if left.head <= right.head:
            return List/Cons(left.head, merge(left.tail, right))
          else:
            return List/Cons(right.head, merge(left, right.tail))

def find_mode(xs, current, current_count, best, best_count):
  match xs:
    case List/Nil:
      if current_count > best_count:
        return current
      else:
        return best
    case List/Cons:
      if xs.head == current:
        return find_mode(xs.tail, current, current_count + 1, best, best_count)
      else:
        if current_count > best_count:
          return find_mode(xs.tail, xs.head, 1, current, current_count)
        else:
          return find_mode(xs.tail, xs.head, 1, best, best_count)
