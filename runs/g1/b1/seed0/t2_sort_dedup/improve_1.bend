def prog(xs):
  return sort_dedup(xs)

def sort_dedup(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          return [xs.head]
        case List/Cons:
          (left, right) = split_alternating(xs)
          sorted_left = sort_dedup(left)
          sorted_right = sort_dedup(right)
          return merge_unique(sorted_left, sorted_right)

def split_alternating(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          return ([xs.head], [])
        case List/Cons:
          (left, right) = split_alternating(tail.tail)
          return (List/Cons(xs.head, left), List/Cons(tail.head, right))

def merge_unique(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if a.head < b.head:
            rest = merge_unique(a.tail, b)
            return List/Cons(a.head, rest)
          else:
            if b.head < a.head:
              rest = merge_unique(a, b.tail)
              return List/Cons(b.head, rest)
            else:
              rest = merge_unique(a.tail, b.tail)
              return List/Cons(a.head, rest)
