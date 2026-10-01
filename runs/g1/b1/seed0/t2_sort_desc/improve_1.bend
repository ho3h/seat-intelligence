def prog(xs):
  return sort_desc(xs)

def sort_desc(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_pairs(xs)
          sorted_left = sort_desc(left)
          sorted_right = sort_desc(right)
          return merge_desc(sorted_left, sorted_right)

def split_pairs(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          return (List/Cons(xs.head, List/Nil), List/Nil)
        case List/Cons:
          (left, right) = split_pairs(tail.tail)
          return (List/Cons(xs.head, left), List/Cons(tail.head, right))

def merge_desc(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if a.head >= b.head:
            return List/Cons(a.head, merge_desc(a.tail, b))
          else:
            return List/Cons(b.head, merge_desc(a, b.tail))
