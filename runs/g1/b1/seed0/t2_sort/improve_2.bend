def prog(xs):
  return quick_sort(xs, 24)

def quick_sort(xs, depth):
  if depth == 0:
    return merge_sort(xs)
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        match xs.tail:
          case List/Nil:
            return xs
          case List/Cons:
            pivot = middle(xs, xs)
            (less, equal, greater) = partition(xs, pivot)
            sorted_less = quick_sort(less, depth - 1)
            sorted_greater = quick_sort(greater, depth - 1)
            return append(sorted_less, append(equal, sorted_greater))

def middle(slow, fast):
  match fast:
    case List/Nil:
      return slow.head
    case List/Cons:
      match fast.tail:
        case List/Nil:
          return slow.head
        case List/Cons:
          return middle(slow.tail, fast.tail.tail)

def partition(xs, pivot):
  match xs:
    case List/Nil:
      return ([], [], [])
    case List/Cons:
      (less, equal, greater) = partition(xs.tail, pivot)
      if xs.head < pivot:
        return (List/Cons(xs.head, less), equal, greater)
      else:
        if xs.head == pivot:
          return (less, List/Cons(xs.head, equal), greater)
        else:
          return (less, equal, List/Cons(xs.head, greater))

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))

def merge_sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split(xs, 0)
          return merge(merge_sort(left), merge_sort(right))

def split(xs, flag):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split(xs.tail, 1 - flag)
      if flag == 0:
        return (List/Cons(xs.head, left), right)
      else:
        return (left, List/Cons(xs.head, right))

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
