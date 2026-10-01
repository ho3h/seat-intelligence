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

def insert_tree(tree, width, start, length, value):
  if width == 1:
    if start >= length:
      return (value, 1)
    else:
      return (value, 0)
  else:
    (left, right, first) = tree
    half = width / 2
    right_start = start + half
    if right_start >= length:
      (new_left, grew) = insert_tree(left, half, start, length, value)
      new_first = first_value(new_left, half)
      return ((new_left, right, new_first), grew)
    else:
      right_first = first_value(right, half)
      if right_first >= value:
        (new_left, grew) = insert_tree(left, half, start, length, value)
        new_first = first_value(new_left, half)
        return ((new_left, right, new_first), grew)
      else:
        (new_right, grew) = insert_tree(right, half, right_start, length, value)
        return ((left, new_right, first), grew)

def process(xs, tree, cap, length):
  match xs:
    case List/Nil:
      return length
    case List/Cons:
      (new_tree, grew) = insert_tree(tree, cap, 0, length, xs.head)
      return process(xs.tail, new_tree, cap, length + grew)
