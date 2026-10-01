def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)

def build_bal(n, xs):
  if n == 0:
    return (Gtree/C0, xs)
  else:
    left_n = (n - 1) / 2
    right_n = n / 2
    (left, rest1) = build_bal(left_n, xs)
    match rest1:
      case List/Nil:
        return (Gtree/C0, List/Nil)
      case List/Cons:
        root = rest1.head
        rest2 = rest1.tail
        (right, rest3) = build_bal(right_n, rest2)
        return (Gtree/C1(left, root, right), rest3)

def prog(xs):
  n = list_len(xs)
  (tree, rest) = build_bal(n, xs)
  return tree
