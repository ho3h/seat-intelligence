def prog(x):
  (n, edges) = x
  if n == 0:
    return 0
  else:
    cap = capacity(n, 1)
    tree = make_tree(n, cap, 0)
    return process_edges(edges, tree, cap, 1)

def capacity(n, span):
  if span < n:
    return capacity(n, span * 2)
  else:
    return span

def make_tree(n, span, offset):
  if span == 1:
    if offset < n:
      return (0, offset, 1)
    else:
      return (0, 0, 0)
  else:
    half = span / 2
    left = make_tree(n, half, offset)
    right = make_tree(n, half, offset + half)
    return (1, left, right)

def get_leaf(tree, index, span):
  if span == 1:
    return tree
  else:
    (tag, left, right) = tree
    half = span / 2
    if index < half:
      return get_leaf(left, index, half)
    else:
      return get_leaf(right, index - half, half)

def set_leaf(tree, index, parent, size, span):
  if span == 1:
    return (0, parent, size)
  else:
    (tag, left, right) = tree
    half = span / 2
    if index < half:
      return (1, set_leaf(left, index, parent, size, half), right)
    else:
      return (1, left, set_leaf(right, index - half, parent, size, half))

def set_two(tree, index_a, parent_a, size_a, index_b, parent_b, size_b, span):
  (tag, left, right) = tree
  half = span / 2
  if index_a < half:
    if index_b < half:
      return (1, set_two(left, index_a, parent_a, size_a, index_b, parent_b, size_b, half), right)
    else:
      next_left = set_leaf(left, index_a, parent_a, size_a, half)
      next_right = set_leaf(right, index_b - half, parent_b, size_b, half)
      return (1, next_left, next_right)
  else:
    if index_b < half:
      next_left = set_leaf(left, index_b, parent_b, size_b, half)
      next_right = set_leaf(right, index_a - half, parent_a, size_a, half)
      return (1, next_left, next_right)
    else:
      return (1, left, set_two(right, index_a - half, parent_a, size_a, index_b - half, parent_b, size_b, half))

def find_root(tree, vertex, cap):
  leaf = get_leaf(tree, vertex, cap)
  (tag, parent, size) = leaf
  if parent == vertex:
    return (vertex, size)
  else:
    return find_root(tree, parent, cap)

def process_edges(edges, tree, cap, best):
  match edges:
    case List/Nil:
      return best
    case List/Cons:
      (u, v) = edges.head
      (root_u, size_u) = find_root(tree, u, cap)
      (root_v, size_v) = find_root(tree, v, cap)
      if root_u == root_v:
        return process_edges(edges.tail, tree, cap, best)
      else:
        combined = size_u + size_v
        if size_u >= size_v:
          next_tree = set_two(tree, root_u, root_u, combined, root_v, root_u, size_v, cap)
        else:
          next_tree = set_two(tree, root_v, root_v, combined, root_u, root_v, size_u, cap)
        if combined > best:
          next_best = combined
        else:
          next_best = best
        return process_edges(edges.tail, next_tree, cap, next_best)
