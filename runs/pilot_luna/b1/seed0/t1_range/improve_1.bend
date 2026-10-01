def prog(n):
  return range_balanced(0, n)

def range_balanced(start, count):
  if count == 0:
    return []
  else:
    if count == 1:
      return List/Cons(start, [])
    else:
      left_count = count / 2
      right_count = count - left_count
      left = range_balanced(start, left_count)
      right = range_balanced(start + left_count, right_count)
      return append_lists(left, right)

def append_lists(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append_lists(xs.tail, ys))
