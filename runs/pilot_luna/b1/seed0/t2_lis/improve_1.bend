def prog(xs):
  n = list_length(xs)
  cap = find_capacity(n, 1)
  tree = build_tree(cap)
  return process(xs, tree, cap, 0)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def find_capacity(n, cap):
  if cap >= n:
    return cap
  else:
    return find_capacity(n, cap * 2)

def build_tree(width):
  if width == 1:
    return 16777215
  else:
    half = width / 2
    left = build_tree(half)
    right = build_tree(half)
    return (left, right, 16777215)

def first_value(tree, width):
  if width == 1:
    return tree
  else:
    (left, right, first) = tree
    return first

def lower_bound(tree, width, start, length, value):
  if width == 1:
    if tree >= value:
      return start
    else:
      return start + 1
  else:
    (left, right, first) = tree
    half = width / 2
    right_start = start + half
    if right_start >= length:
      return lower_bound(left, half, start, length, value)
    else:
      right_first = first_value(right, half)
      if right_first >= value:
        return lower_bound(left, half, start, length, value)
      else:
        return lower_bound(right, half, right_start, length, value)

def update_tree(tree, width, index, value):
  if width == 1:
    return value
  else:
    (left, right, first) = tree
    half = width / 2
    if index < half:
      new_left = update_tree(left, half, index, value)
      new_first = first_value(new_left, half)
      return (new_left, right, new_first)
    else:
      new_right = update_tree(right, half, index - half, value)
      return (left, new_right, first)

def process(xs, tree, cap, length):
  match xs:
    case List/Nil:
      return length
    case List/Cons:
      index = lower_bound(tree, cap, 0, length, xs.head)
      new_tree = update_tree(tree, cap, index, xs.head)
      if index == length:
        return process(xs.tail, new_tree, cap, length + 1)
      else:
        return process(xs.tail, new_tree, cap, length)
