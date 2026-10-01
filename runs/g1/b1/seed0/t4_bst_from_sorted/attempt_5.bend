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

def list_head(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return xs.head

def list_tail(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      return xs.tail

def build_tree(xs, n):
  if n == 0:
    return Gtree/C0
  else:
    left_n = (n - 1) / 2
    middle = drop_n(xs, left_n)
    value = list_head(middle)
    right_xs = list_tail(middle)
    right_n = n - left_n - 1
    left = build_tree(take_n(xs, left_n), left_n)
    right = build_tree(right_xs, right_n)
    return Gtree/C1(left, value, right)
