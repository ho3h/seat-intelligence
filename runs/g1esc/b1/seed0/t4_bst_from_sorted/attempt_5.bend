def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)

def build_rec_with_rest(n, xs):
  if n == 0:
    return (Gtree/C0, xs)
  else:
    left_n = (n - 1) / 2
    right_n = n / 2
    (left_tree, rest1) = build_rec_with_rest(left_n, xs)
    match rest1:
      case List/Nil:
        return (Gtree/C0, List/Nil)
      case List/Cons:
        root = rest1.head
        (right_tree, rest2) = build_rec_with_rest(right_n, rest1.tail)
        return (Gtree/C1(left_tree, root, right_tree), rest2)

def prog(xs):
  n = list_len(xs)
  (tree, rest) = build_rec_with_rest(n, xs)
  return tree
