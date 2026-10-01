def prog(xs):
  n = list_length(xs)
  return build_tree(xs, n)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def take_n(xs, n):
  if n == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(xs.head, take_n(xs.tail, n - 1))

def drop_n(xs, n):
  if n == 0:
    return xs
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return drop_n(xs.tail, n - 1)

def build_tree(xs, n):
  if n == 0:
    return Gtree/C0
  else:
    left_n = (n - 1) / 2
    left_xs = take_n(xs, left_n)
    from_root = drop_n(xs, left_n)
    match from_root:
      case List/Nil:
        return Gtree/C0
      case List/Cons:
        value = from_root.head
        right_xs = from_root.tail
        right_n = n - left_n - 1
        left = build_tree(left_xs, left_n)
        right = build_tree(right_xs, right_n)
        return Gtree/C1(left, value, right)
