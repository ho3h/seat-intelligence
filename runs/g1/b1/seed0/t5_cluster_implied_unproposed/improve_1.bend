def make_parent_tree(lo, hi):
  if lo == hi:
    return 0
  else:
    if hi - lo == 1:
      return lo
    else:
      mid = lo + (hi - lo) / 2
      left = make_parent_tree(lo, mid)
      right = make_parent_tree(mid, hi)
      return (left, right)

def make_size_tree(lo, hi):
  if lo == hi:
    return 0
  else:
    if hi - lo == 1:
      return 1
    else:
      mid = lo + (hi - lo) / 2
      left = make_size_tree(lo, mid)
      right = make_size_tree(mid, hi)
      return (left, right)

def make_zero_tree(lo, hi):
  if lo == hi:
    return 0
  else:
    if hi - lo == 1:
      return 0
    else:
      mid = lo + (hi - lo) / 2
      left = make_zero_tree(lo, mid)
      right = make_zero_tree(mid, hi)
      return (left, right)

def make_seen_tree(lo, hi, n):
  if lo == hi:
    return 0
  else:
    if hi - lo == 1:
      return make_zero_tree(0, n)
    else:
      mid = lo + (hi - lo) / 2
      left = make_seen_tree(lo, mid, n)
      right = make_seen_tree(mid, hi, n)
      return (left, right)

def tree_get(tree, lo, hi, index):
  if hi - lo == 1:
    return tree
  else:
    mid = lo + (hi - lo) / 2
    (left, right) = tree
    if index < mid:
      return tree_get(left, lo, mid, index)
    else:
      return tree_get(right, mid, hi, index)

def tree_put(tree, lo, hi, index, value):
  if hi - lo == 1:
    return value
  else:
    mid = lo + (hi - lo) / 2
    (left, right) = tree
    if index < mid:
      left2 = tree_put(left, lo, mid, index, value)
      return (left2, right)
    else:
      right2 = tree_put(right, mid, hi, index, value)
      return (left, right2)

def find_root(parents, n, node):
  parent = tree_get(parents, 0, n, node)
  if parent == node:
    return node
  else:
    return find_root(parents, n, parent)

def process_edges(edges, parents, sizes, seen, n, distinct):
  match edges:
    case List/Nil:
      return ((parents, sizes), (seen, distinct))
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(parents, n, u)
      root_v = find_root(parents, n, v)

      if root_u == root_v:
        parents2 = parents
        sizes2 = sizes
      else:
        size_u = tree_get(sizes, 0, n, root_u)
        size_v = tree_get(sizes, 0, n, root_v)
        if size_u < size_v:
          parents2 = tree_put(parents, 0, n, root_u, root_v)
          new_size = size_u + size_v
          sizes2 = tree_put(sizes, 0, n, root_v, new_size)
        else:
          parents2 = tree_put(parents, 0, n, root_v, root_u)
          new_size = size_u + size_v
          sizes2 = tree_put(sizes, 0, n, root_u, new_size)

      row = tree_get(seen, 0, n, u)
      present = tree_get(row, 0, n, v)
      if present == 0:
        row2 = tree_put(row, 0, n, v, 1)
        seen2 = tree_put(seen, 0, n, u, row2)
        return process_edges(edges.tail, parents2, sizes2, seen2, n, distinct + 1)
      else:
        return process_edges(edges.tail, parents2, sizes2, seen, n, distinct)

def sum_root_pairs(parents, sizes, n, i, total):
  if i == n:
    return total
  else:
    parent = tree_get(parents, 0, n, i)
    if parent == i:
      size = tree_get(sizes, 0, n, i)
      pairs = (size * (size - 1)) / 2
      return sum_root_pairs(parents, sizes, n, i + 1, total + pairs)
    else:
      return sum_root_pairs(parents, sizes, n, i + 1, total)

def prog(x):
  (n, edges) = x
  parents = make_parent_tree(0, n)
  sizes = make_size_tree(0, n)
  seen = make_seen_tree(0, n, n)
  state = process_edges(edges, parents, sizes, seen, n, 0)
  (arrays, counts) = state
  (final_parents, final_sizes) = arrays
  (final_seen, distinct) = counts
  total = sum_root_pairs(final_parents, final_sizes, n, 0, 0)
  return total - distinct
