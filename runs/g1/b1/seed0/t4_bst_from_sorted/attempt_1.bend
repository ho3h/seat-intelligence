def prog(xs):
  n = list_length(xs)
  (tree, rest) = build_n(xs, n)
  return tree

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def build_n(xs, n):
  if n == 0:
    return (Gtree/C0, xs)
  else:
    left_n = (n - 1) / 2
    (left, remaining) = build_n(xs, left_n)
    match remaining:
      case List/Nil:
        return (Gtree/C0, List/Nil)
      case List/Cons:
        value = remaining.head
        right_n = n - left_n - 1
        (right, rest) = build_n(remaining.tail, right_n)
        return (Gtree/C1(left, value, right), rest)
