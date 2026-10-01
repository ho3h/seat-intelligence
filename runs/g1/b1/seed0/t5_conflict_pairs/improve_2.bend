def prog(x):
  (c, mnl) = x
  n = list_length(c)
  (tree, rest) = build_tree(c, n)
  violations = collect_violations(tree, n, mnl)
  return merge_sort(violations)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def build_tree(xs, n):
  if n == 0:
    return (0, xs)
  else:
    if n == 1:
      match xs:
        case List/Nil:
          return ((1, 0, 0), List/Nil)
        case List/Cons:
          return ((1, xs.head, 0), xs.tail)
    else:
      left_n = n / 2
      right_n = n - left_n
      (left_tree, rest) = build_tree(xs, left_n)
      (right_tree, rest2) = build_tree(rest, right_n)
      return ((0, left_tree, right_tree), rest2)

def tree_get(tree, n, index):
  if n == 1:
    (tag, value, other) = tree
    return value
  else:
    (tag, left_tree, right_tree) = tree
    left_n = n / 2
    if index < left_n:
      return tree_get(left_tree, left_n, index)
    else:
      return tree_get(right_tree, n - left_n, index - left_n)

def collect_violations(tree, n, pairs):
  match pairs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (a, b) = pairs.head
      if tree_get(tree, n, a) == tree_get(tree, n, b):
        return List/Cons(pairs.head, collect_violations(tree, n, pairs.tail))
      else:
        return collect_violations(tree, n, pairs.tail)

def split_pairs(xs, side, left, right):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if side == 0:
        return split_pairs(xs.tail, 1, List/Cons(xs.head, left), right)
      else:
        return split_pairs(xs.tail, 0, left, List/Cons(xs.head, right))

def pair_leq(p, q):
  (a, b) = p
  (c, d) = q
  if a < c:
    return 1
  else:
    if a == c:
      if b <= d:
        return 1
      else:
        return 0
    else:
      return 0

def merge_pairs(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if pair_leq(xs.head, ys.head) == 1:
            return List/Cons(xs.head, merge_pairs(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge_pairs(xs, ys.tail))

def merge_sort(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_pairs(xs, 0, List/Nil, List/Nil)
          sorted_left = merge_sort(left)
          sorted_right = merge_sort(right)
          return merge_pairs(sorted_left, sorted_right)
