type IdxTree: Leaf { value } | Branch { split, left, right }

def prog(x):
  (c, mnl) = x
  n = list_size(c)
  c_tree = build_tree(c, n)
  flags = build_zero_tree(n)
  marked = mark_pairs(mnl, c_tree, flags)
  return emit_flags(c, marked, 0)

def list_size(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_size(xs.tail)

def reverse_list(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))

def split_prefix(xs, count, acc):
  if count == 0:
    return (reverse_list(acc), xs)
  else:
    match xs:
      case List/Nil:
        return (reverse_list(acc), [])
      case List/Cons:
        return split_prefix(xs.tail, count - 1, List/Cons(xs.head, acc))

def build_tree(xs, size):
  if size <= 1:
    match xs:
      case List/Nil:
        return IdxTree/Leaf(0)
      case List/Cons:
        return IdxTree/Leaf(xs.head)
  else:
    left_size = size / 2
    (left_items, right_items) = split_prefix(xs, left_size, [])
    left_tree = build_tree(left_items, left_size)
    right_tree = build_tree(right_items, size - left_size)
    return IdxTree/Branch(left_size, left_tree, right_tree)

def build_zero_tree(size):
  if size <= 1:
    return IdxTree/Leaf(0)
  else:
    left_size = size / 2
    left_tree = build_zero_tree(left_size)
    right_tree = build_zero_tree(size - left_size)
    return IdxTree/Branch(left_size, left_tree, right_tree)

def tree_get(tree, index):
  match tree:
    case IdxTree/Leaf:
      return tree.value
    case IdxTree/Branch:
      if index < tree.split:
        return tree_get(tree.left, index)
      else:
        return tree_get(tree.right, index - tree.split)

def tree_set(tree, index, value):
  match tree:
    case IdxTree/Leaf:
      return IdxTree/Leaf(value)
    case IdxTree/Branch:
      if index < tree.split:
        left_tree = tree_set(tree.left, index, value)
        return IdxTree/Branch(tree.split, left_tree, tree.right)
      else:
        right_tree = tree_set(tree.right, index - tree.split, value)
        return IdxTree/Branch(tree.split, tree.left, right_tree)

def mark_pairs(pairs, c_tree, flags):
  match pairs:
    case List/Nil:
      return flags
    case List/Cons:
      (a, b) = pairs.head
      ca = tree_get(c_tree, a)
      cb = tree_get(c_tree, b)
      if ca == cb:
        if tree_get(flags, ca) == 1:
          return mark_pairs(pairs.tail, c_tree, flags)
        else:
          new_flags = tree_set(flags, ca, 1)
          return mark_pairs(pairs.tail, c_tree, new_flags)
      else:
        return mark_pairs(pairs.tail, c_tree, flags)

def emit_flags(xs, flags, index):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      rest = emit_flags(xs.tail, flags, index + 1)
      if xs.head == index:
        flag = tree_get(flags, index)
        return List/Cons(flag, rest)
      else:
        return rest
