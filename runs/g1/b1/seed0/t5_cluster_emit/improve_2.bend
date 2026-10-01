def prog(x):
  (n, pairs) = x
  width = capacity(n, 1)
  tree = build_tree(0, width, n)
  merged = process_edges(pairs, tree, width)
  return emit(merged, 0, n, width)

def capacity(n, width):
  if width >= n:
    return width
  else:
    return capacity(n, width * 2)

def build_tree(start, width, n):
  if width == 1:
    if start < n:
      return (start, 1, start)
    else:
      return (0, 0, 0)
  else:
    half = width / 2
    left = build_tree(start, half, n)
    right = build_tree(start + half, half, n)
    return (left, right)

def tree_get(tree, index, width):
  if width == 1:
    return tree
  else:
    (left, right) = tree
    half = width / 2
    if index < half:
      return tree_get(left, index, half)
    else:
      return tree_get(right, index - half, half)

def tree_set(tree, index, width, value):
  if width == 1:
    return value
  else:
    (left, right) = tree
    half = width / 2
    if index < half:
      updated = tree_set(left, index, half, value)
      return (updated, right)
    else:
      updated = tree_set(right, index - half, half, value)
      return (left, updated)

def find_compress(tree, index, width):
  record = tree_get(tree, index, width)
  (parent, size, maximum) = record
  if parent == index:
    return (index, tree)
  else:
    (root, updated_tree) = find_compress(tree, parent, width)
    if parent == root:
      return (root, updated_tree)
    else:
      current = tree_get(updated_tree, index, width)
      (_, current_size, current_maximum) = current
      compressed = tree_set(updated_tree, index, width, (root, current_size, current_maximum))
      return (root, compressed)

def find_root(tree, index, width):
  record = tree_get(tree, index, width)
  (parent, size, maximum) = record
  if parent == index:
    return index
  else:
    return find_root(tree, parent, width)

def process_edges(pairs, tree, width):
  match pairs:
    case List/Nil:
      return tree
    case List/Cons:
      (u, v) = pairs.head
      (root_u, after_u) = find_compress(tree, u, width)
      (root_v, after_v) = find_compress(after_u, v, width)
      if root_u == root_v:
        return process_edges(pairs.tail, after_v, width)
      else:
        record_u = tree_get(after_v, root_u, width)
        record_v = tree_get(after_v, root_v, width)
        (parent_u, size_u, max_u) = record_u
        (parent_v, size_v, max_v) = record_v
        if size_u >= size_v:
          if max_u >= max_v:
            new_max = max_u
          else:
            new_max = max_v
          updated_winner = tree_set(after_v, root_u, width, (root_u, size_u + size_v, new_max))
          updated = tree_set(updated_winner, root_v, width, (root_u, size_v, max_v))
          return process_edges(pairs.tail, updated, width)
        else:
          if max_u >= max_v:
            new_max = max_u
          else:
            new_max = max_v
          updated_winner = tree_set(after_v, root_v, width, (root_v, size_u + size_v, new_max))
          updated = tree_set(updated_winner, root_u, width, (root_v, size_u, max_u))
          return process_edges(pairs.tail, updated, width)

def emit(tree, index, n, width):
  if index == n:
    return []
  else:
    tail = emit(tree, index + 1, n, width)
    root = find_root(tree, index, width)
    record = tree_get(tree, root, width)
    (parent, size, canonical) = record
    if index == canonical:
      return tail
    else:
      return List/Cons((index, canonical), tail)
