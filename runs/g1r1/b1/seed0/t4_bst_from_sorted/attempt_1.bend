def prog(xs):
  n = len_list(xs)
  (tree, rest) = build(xs, n)
  return tree

def len_list(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + len_list(xs.tail)

def build(xs, n):
  if n == 0:
    return (Gtree/C0, xs)
  else:
    left_n = (n - 1) / 2
    (left, rest1) = build(xs, left_n)
    match rest1:
      case List/Nil:
        return (Gtree/C0, List/Nil)
      case List/Cons:
        right_n = n - left_n - 1
        (right, rest2) = build(rest1.tail, right_n)
        return (Gtree/C1(left, rest1.head, right), rest2)
