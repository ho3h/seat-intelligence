def prog(x):
  (c, attrs) = x
  n = length(c)
  size = next_power(n, 1)
  (tree, rest) = make_tree(c, size)
  mapped = map_attrs(attrs, tree, size)
  return emit_range(mapped, 0, size)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def next_power(n, p):
  if p >= n:
    return p
  else:
    return next_power(n, p * 2)

def make_tree(xs, size):
  if size == 1:
    match xs:
      case List/Nil:
        return ((0, 0), [])
      case List/Cons:
        return ((xs.head, 0), xs.tail)
  else:
    half = size / 2
    (left, rest) = make_tree(xs, half)
    (right, rest2) = make_tree(rest, half)
    return ((left, right), rest2)

def tree_get(tree, index, size):
  if size == 1:
    (value, dummy) = tree
    return value
  else:
    (left, right) = tree
    half = size / 2
    if index < half:
      return tree_get(left, index, half)
    else:
      return tree_get(right, index - half, half)

def map_attrs(attrs, tree, size):
  match attrs:
    case List/Nil:
      return []
    case List/Cons:
      (node, key, value) = attrs.head
      cid = tree_get(tree, node, size)
      rest = map_attrs(attrs.tail, tree, size)
      return List/Cons((cid, key, value), rest)

def partition(attrs, pivot, low, high):
  match attrs:
    case List/Nil:
      return (low, high)
    case List/Cons:
      (cid, key, value) = attrs.head
      if cid < pivot:
        return partition(attrs.tail, pivot, List/Cons(attrs.head, low), high)
      else:
        return partition(attrs.tail, pivot, low, List/Cons(attrs.head, high))

def has_conflict(attrs, key, seen, old_value):
  match attrs:
    case List/Nil:
      return 0
    case List/Cons:
      (cid, attr_key, value) = attrs.head
      if attr_key == key:
        if seen == 0:
          return has_conflict(attrs.tail, key, 1, value)
        else:
          if value != old_value:
            return 1
          else:
            return has_conflict(attrs.tail, key, seen, old_value)
      else:
        return has_conflict(attrs.tail, key, seen, old_value)

def emit_keys(attrs, cid, key):
  if key == 4:
    return []
  else:
    if has_conflict(attrs, key, 0, 0) == 1:
      return List/Cons((cid, key), emit_keys(attrs, cid, key + 1))
    else:
      return emit_keys(attrs, cid, key + 1)

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))

def emit_range(attrs, lo, size):
  match attrs:
    case List/Nil:
      return []
    case List/Cons:
      if size == 1:
        return emit_keys(attrs, lo, 0)
      else:
        half = size / 2
        pivot = lo + half
        (low, high) = partition(attrs, pivot, [], [])
        left = emit_range(low, lo, half)
        right = emit_range(high, pivot, half)
        return append(left, right)
