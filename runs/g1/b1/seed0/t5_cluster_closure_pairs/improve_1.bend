def prog(x):
  (n, pairs) = x
  if n == 0:
    return 0
  else:
    parents = build_tree(0, n, 0)
    sizes = build_tree(0, n, 1)
    (final_parents, final_sizes) = process_edges(pairs, parents, sizes, n)
    return count_roots(final_parents, final_sizes, 0, n)

def build_tree(lo, hi, kind):
  if hi - lo == 1:
    if kind == 0:
      return (0, lo)
    else:
      return (0, 1)
  else:
    mid = (lo + hi) / 2
    left = build_tree(lo, mid, kind)
    right = build_tree(mid, hi, kind)
    return (1, (left, right))

def tree_get(tree, lo, hi, index):
  (tag, payload) = tree
  if tag == 0:
    return payload
  else:
    (left, right) = payload
    mid = (lo + hi) / 2
    if index < mid:
      return tree_get(left, lo, mid, index)
    else:
      return tree_get(right, mid, hi, index)

def tree_set(tree, lo, hi, index, value):
  (tag, payload) = tree
  if tag == 0:
    return (0, value)
  else:
    (left, right) = payload
    mid = (lo + hi) / 2
    if index < mid:
      new_left = tree_set(left, lo, mid, index, value)
      return (1, (new_left, right))
    else:
      new_right = tree_set(right, mid, hi, index, value)
      return (1, (left, new_right))

def find_root(parents, node, n):
  parent = tree_get(parents, 0, n, node)
  if parent == node:
    return node
  else:
    return find_root(parents, parent, n)

def process_edges(edges, parents, sizes, n):
  match edges:
    case List/Nil:
      return (parents, sizes)
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(parents, u, n)
      root_v = find_root(parents, v, n)
      if root_u == root_v:
        return process_edges(edges.tail, parents, sizes, n)
      else:
        size_u = tree_get(sizes, 0, n, root_u)
        size_v = tree_get(sizes, 0, n, root_v)
        if size_u < size_v:
          parents2 = tree_set(parents, 0, n, root_u, root_v)
          sizes2 = tree_set(sizes, 0, n, root_v, size_u + size_v)
          return process_edges(edges.tail, parents2, sizes2, n)
        else:
          parents2 = tree_set(parents, 0, n, root_v, root_u)
          sizes2 = tree_set(sizes, 0, n, root_u, size_u + size_v)
          return process_edges(edges.tail, parents2, sizes2, n)

def count_roots(parents, sizes, i, n):
  if i == n:
    return 0
  else:
    parent = tree_get(parents, 0, n, i)
    if parent == i:
      size = tree_get(sizes, 0, n, i)
      return size * (size - 1) / 2 + count_roots(parents, sizes, i + 1, n)
    else:
      return count_roots(parents, sizes, i + 1, n)
