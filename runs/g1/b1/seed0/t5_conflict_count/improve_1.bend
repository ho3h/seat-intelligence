def prog(x):
  (c, pairs) = x
  n = list_length(c)
  if n == 0:
    return 0
  else:
    tree = build_tree(c, n)
    return count_conflicts(tree, n, pairs)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def build_tree(xs, n):
  (tree, rest) = build_from(xs, n)
  return tree

def build_from(xs, n):
  if n == 1:
    match xs:
      case List/Nil:
        return (0, [])
      case List/Cons:
        return (xs.head, xs.tail)
  else:
    k = n / 2
    (left, rem) = build_from(xs, k)
    (right, rest) = build_from(rem, n - k)
    return ((left, right), rest)

def get_tree(tree, n, i):
  if n == 1:
    return tree
  else:
    (left, right) = tree
    k = n / 2
    if i < k:
      return get_tree(left, k, i)
    else:
      return get_tree(right, n - k, i - k)

def same_cluster(tree, n, a, b):
  (left, right) = tree
  k = n / 2
  if b < k:
    return same_cluster(left, k, a, b)
  else:
    if a >= k:
      return same_cluster(right, n - k, a - k, b - k)
    else:
      return get_tree(left, k, a) == get_tree(right, n - k, b - k)

def count_conflicts(tree, n, pairs):
  match pairs:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = pairs.head
      if same_cluster(tree, n, a, b):
        return 1 + count_conflicts(tree, n, pairs.tail)
      else:
        return count_conflicts(tree, n, pairs.tail)
