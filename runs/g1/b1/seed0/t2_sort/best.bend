def prog(xs):
  return sort(xs)

def sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split(xs, 0)
          return merge(sort(left), sort(right))

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
