type IdxTree: Leaf { value } | Branch { split, left, right }

def prog(x):
  (c, mnl) = x
  n = list_size(c)
  if n == 0:
    return []
  else:
    (c_tree, _) = build_tree_stream(c, n)
    flags = mark_pairs(mnl, c_tree, (0, 0, 0, 0, 0, 0))
    return emit_flags(c, flags, 0)

def list_size(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_size(xs.tail)

def build_tree_stream(xs, size):
  if size == 0:
    return (IdxTree/Leaf(0), xs)
  else:
    if size == 1:
      match xs:
        case List/Nil:
          return (IdxTree/Leaf(0), [])
        case List/Cons:
          return (IdxTree/Leaf(xs.head), xs.tail)
    else:
      left_size = size / 2
      (left_tree, rest) = build_tree_stream(xs, left_size)
      (right_tree, rest2) = build_tree_stream(rest, size - left_size)
      return (IdxTree/Branch(left_size, left_tree, right_tree), rest2)

def tree_get(tree, index):
  match tree:
    case IdxTree/Leaf:
      return tree.value
    case IdxTree/Branch:
      if index < tree.split:
        return tree_get(tree.left, index)
      else:
        return tree_get(tree.right, index - tree.split)

def mark_pairs(pairs, c_tree, flags):
  match pairs:
    case List/Nil:
      return flags
    case List/Cons:
      (a, b) = pairs.head
      ca = tree_get(c_tree, a)
      cb = tree_get(c_tree, b)
      if ca == cb:
        new_flags = set_flag(flags, ca)
        return mark_pairs(pairs.tail, c_tree, new_flags)
      else:
        return mark_pairs(pairs.tail, c_tree, flags)

def set_flag(flags, index):
  (f0, f1, f2, f3, f4, f5) = flags
  block = index / 24
  bit = 1 << (index % 24)
  if block == 0:
    return (f0 | bit, f1, f2, f3, f4, f5)
  else:
    if block == 1:
      return (f0, f1 | bit, f2, f3, f4, f5)
    else:
      if block == 2:
        return (f0, f1, f2 | bit, f3, f4, f5)
      else:
        if block == 3:
          return (f0, f1, f2, f3 | bit, f4, f5)
        else:
          if block == 4:
            return (f0, f1, f2, f3, f4 | bit, f5)
          else:
            return (f0, f1, f2, f3, f4, f5 | bit)

def get_flag(flags, index):
  (f0, f1, f2, f3, f4, f5) = flags
  block = index / 24
  bit = 1 << (index % 24)
  if block == 0:
    if (f0 & bit) != 0:
      return 1
    else:
      return 0
  else:
    if block == 1:
      if (f1 & bit) != 0:
        return 1
      else:
        return 0
    else:
      if block == 2:
        if (f2 & bit) != 0:
          return 1
        else:
          return 0
      else:
        if block == 3:
          if (f3 & bit) != 0:
            return 1
          else:
            return 0
        else:
          if block == 4:
            if (f4 & bit) != 0:
              return 1
            else:
              return 0
          else:
            if (f5 & bit) != 0:
              return 1
            else:
              return 0

def emit_flags(xs, flags, index):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      rest = emit_flags(xs.tail, flags, index + 1)
      if xs.head == index:
        return List/Cons(get_flag(flags, index), rest)
      else:
        return rest
