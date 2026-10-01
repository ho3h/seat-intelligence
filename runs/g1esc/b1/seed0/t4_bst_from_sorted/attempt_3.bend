def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)

def take(n, xs):
  if n == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(xs.head, take(n - 1, xs.tail))

def drop(n, xs):
  if n == 0:
    return xs
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return drop(n - 1, xs.tail)

def build_rec(n, xs):
  if n == 0:
    return Gtree/C0
  else:
    left_n = (n - 1) / 2
    right_n = n / 2
    left_part = take(left_n, xs)
    after_left = drop(left_n, xs)
    left_tree = build_rec(left_n, left_part)
    match after_left:
      case List/Nil:
        return Gtree/C0
      case List/Cons:
        root = after_left.head
        right_part = after_left.tail
        right_tree = build_rec(right_n, right_part)
        return Gtree/C1(left_tree, root, right_tree)

def prog(xs):
  n = list_len(xs)
  return build_rec(n, xs)
