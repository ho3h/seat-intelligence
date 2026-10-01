def prog(xs):
  n = list_size(xs)
  if n == 0:
    return 0
  else:
    (tree, rest) = build_tree(xs, n)
    return check_range(tree, n, 0, n)

def list_size(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_size(xs.tail)

def build_tree(xs, size):
  if size == 1:
    match xs:
      case List/Nil:
        return (0, xs)
      case List/Cons:
        return (xs.head, xs.tail)
  else:
    left_size = size / 2
    (left, rest) = build_tree(xs, left_size)
    (right, rest2) = build_tree(rest, size - left_size)
    return ((left, right), rest2)

def get_tree(tree, size, i):
  if size == 1:
    return tree
  else:
    (left, right) = tree
    left_size = size / 2
    if i < left_size:
      return get_tree(left, left_size, i)
    else:
      return get_tree(right, size - left_size, i - left_size)

def check_range(tree, n, start, count):
  if count == 1:
    return brent_start(tree, n, start)
  else:
    left_count = count / 2
    left = check_range(tree, n, start, left_count)
    right = check_range(tree, n, start + left_count, count - left_count)
    return left | right

def brent_start(tree, n, start):
  hare = get_tree(tree, n, get_tree(tree, n, start))
  return brent_loop(tree, n, start, hare, 1, 1)

def brent_loop(tree, n, tortoise, hare, power, lam):
  if tortoise == hare:
    if lam == 1:
      return 0
    else:
      return 1
  else:
    if power == lam:
      next_hare = get_tree(tree, n, hare)
      return brent_loop(tree, n, hare, next_hare, power * 2, 1)
    else:
      next_hare = get_tree(tree, n, hare)
      return brent_loop(tree, n, tortoise, next_hare, power, lam + 1)
