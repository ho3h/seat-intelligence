def prog(x):
  return sort_pairs(x)

def sort_pairs(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          pivot = middle_pair(xs, xs)
          (pivot_key, pivot_value) = pivot
          (less, equal, greater) = partition_pairs(xs, pivot_key)
          sorted_less = sort_pairs(less)
          sorted_greater = sort_pairs(greater)
          equal_and_greater = append_pairs(equal, sorted_greater)
          return append_pairs(sorted_less, equal_and_greater)

def middle_pair(slow, fast):
  match fast:
    case List/Nil:
      return slow.head
    case List/Cons:
      match fast.tail:
        case List/Nil:
          return slow.head
        case List/Cons:
          return middle_pair(slow.tail, fast.tail.tail)

def partition_pairs(xs, pivot_key):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil, List/Nil)
    case List/Cons:
      (key, value) = xs.head
      (less, equal, greater) = partition_pairs(xs.tail, pivot_key)
      if key < pivot_key:
        return (List/Cons(xs.head, less), equal, greater)
      else:
        if key == pivot_key:
          return (less, List/Cons(xs.head, equal), greater)
        else:
          return (less, equal, List/Cons(xs.head, greater))

def append_pairs(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append_pairs(xs.tail, ys))
