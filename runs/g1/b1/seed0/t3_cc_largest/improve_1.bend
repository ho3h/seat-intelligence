def prog(x):
  (n, edges) = x
  cap = capacity(n, 1)
  parents = make_tree(n, cap, 0, 0)
  sizes = make_tree(n, cap, 0, 1)
  if n == 0:
    best = 0
  else:
    best = 1
  (parents, sizes, best) = process_edges(edges, parents, sizes, cap, best)
  return best

def capacity(n, span):
  if span < n:
    return capacity(n, span * 2)
  else:
    return span

def make_tree(n, span, offset, mode):
  if span == 1:
    if offset < n:
      if mode == 0:
        return (0, offset, 0)
      else:
        return (0, 1, 0)
    else:
      return (0, 0, 0)
  else:
    half = span / 2
    left = make_tree(n, half, offset, mode)
    right = make_tree(n, half, offset + half, mode)
    return (1, left, right)

def get_tree(tree, index, span):
  (tag, left, right) = tree
  if span == 1:
    return left
  else:
    half = span / 2
    if index < half:
      return get_tree(left, index, half)
    else:
      return get_tree(right, index - half, half)

def set_tree(tree, index, value, span):
  (tag, left, right) = tree
  if span == 1:
    return (0, value, 0)
  else:
    half = span / 2
    if index < half:
      return (1, set_tree(left, index, value, half), right)
    else:
      return (1, left, set_tree(right, index - half, value, half))

def find_root(parents, vertex, cap):
  parent = get_tree(parents, vertex, cap)
  if parent == vertex:
    return vertex
  else:
    return find_root(parents, parent, cap)

def process_edges(edges, parents, sizes, cap, best):
  match edges:
    case List/Nil:
      return (parents, sizes, best)
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(parents, u, cap)
      root_v = find_root(parents, v, cap)
      if root_u == root_v:
        return process_edges(edges.tail, parents, sizes, cap, best)
      else:
        size_u = get_tree(sizes, root_u, cap)
        size_v = get_tree(sizes, root_v, cap)
        combined = size_u + size_v
        if size_u >= size_v:
          next_parents = set_tree(parents, root_v, root_u, cap)
          next_sizes = set_tree(sizes, root_u, combined, cap)
        else:
          next_parents = set_tree(parents, root_u, root_v, cap)
          next_sizes = set_tree(sizes, root_v, combined, cap)
        if combined > best:
          next_best = combined
        else:
          next_best = best
        return process_edges(edges.tail, next_parents, next_sizes, cap, next_best)
