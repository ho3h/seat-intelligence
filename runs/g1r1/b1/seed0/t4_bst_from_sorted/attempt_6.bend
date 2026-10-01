def prog(xs):
  n = len_list(xs)
  return build(xs, n)

def len_list(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + len_list(xs.tail)

def split_at(xs, n):
  if n == 0:
    return ([], xs)
  else:
    match xs:
      case List/Nil:
        return ([], List/Nil)
      case List/Cons:
        (prefix, suffix) = split_at(xs.tail, n - 1)
        return (List/Cons(xs.head, prefix), suffix)

def uncons(xs):
  match xs:
    case List/Nil:
      return (0, List/Nil)
    case List/Cons:
      return (xs.head, xs.tail)

def build(xs, n):
  if n == 0:
    return Gtree/C0
  else:
    left_n = (n - 1) / 2
    (left_xs, rest) = split_at(xs, left_n)
    (root, right_xs) = uncons(rest)
    left = build(left_xs, left_n)
    right_n = n - left_n - 1
    right = build(right_xs, right_n)
    return Gtree/C1(left, root, right)
