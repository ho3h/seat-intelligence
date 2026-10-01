def prog(xs):
  return count_sorted(merge_sort(xs), 0, 0, 0)

def split_alt(xs, flag):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_alt(xs.tail, 1 - flag)
      if flag == 0:
        return (List/Cons(xs.head, left), right)
      else:
        return (left, List/Cons(xs.head, right))

def merge_sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alt(xs, 0)
          return merge(merge_sort(left), merge_sort(right))

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

def count_sorted(xs, previous, have_previous, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if have_previous == 0:
        return count_sorted(xs.tail, xs.head, 1, acc + 1)
      else:
        if xs.head == previous:
          return count_sorted(xs.tail, previous, 1, acc)
        else:
          return count_sorted(xs.tail, xs.head, 1, acc + 1)
