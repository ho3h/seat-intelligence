def prog(p):
  n = length(p)
  if n == 0:
    return []
  else:
    (tree, rest) = build(p, n)
    return solve(tree, n)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def build(xs, n):
  if n == 1:
    match xs:
      case List/Nil:
        return ((0, 0), [])
      case List/Cons:
        return ((xs.head, xs.head), xs.tail)
  else:
    left_n = n / 2
    right_n = n - left_n
    (left, rest1) = build(xs, left_n)
    (right, rest2) = build(rest1, right_n)
    return ((left, right), rest2)

def solve(tree, n):
  (updated, stable) = jump_tree(tree, tree, n, n)
  if stable == 1:
    return flatten(tree, n)
  else:
    return solve(updated, n)

def jump_tree(current, full, total, size):
  if size == 1:
    (old, duplicate) = current
    target = get_tree(full, old, total)
    if old == target:
      return ((target, target), 1)
    else:
      return ((target, target), 0)
  else:
    (left, right) = current
    left_n = size / 2
    right_n = size - left_n
    (new_left, stable_left) = jump_tree(left, full, total, left_n)
    (new_right, stable_right) = jump_tree(right, full, total, right_n)
    return ((new_left, new_right), stable_left * stable_right)

def get_tree(tree, index, size):
  if size == 1:
    (value, duplicate) = tree
    return value
  else:
    (left, right) = tree
    left_n = size / 2
    if index < left_n:
      return get_tree(left, index, left_n)
    else:
      return get_tree(right, index - left_n, size - left_n)

def flatten(tree, size):
  if size == 1:
    (value, duplicate) = tree
    return [value]
  else:
    (left, right) = tree
    left_n = size / 2
    right_n = size - left_n
    return append(flatten(left, left_n), flatten(right, right_n))

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))
