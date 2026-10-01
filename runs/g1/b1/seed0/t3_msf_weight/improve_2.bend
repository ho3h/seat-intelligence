def prog(x):
  (n, edges) = x
  size = tree_size(n, 1)
  dsu = make_dsu(0, size, n)
  return boruvka(n, edges, size, dsu, 0)

def tree_size(n, p):
  if p >= n:
    return p
  else:
    return tree_size(n, p * 2)

def make_dsu(lo, hi, n):
  if hi - lo == 1:
    if lo < n:
      return (0, (lo, 1), 0)
    else:
      return (0, (lo, 1), 0)
  else:
    mid = (lo + hi) / 2
    left = make_dsu(lo, mid, n)
    right = make_dsu(mid, hi, n)
    return (1, left, right)

def make_best_tree(lo, hi):
  if hi - lo == 1:
    return (0, (0, 0, 0, 0), 0)
  else:
    mid = (lo + hi) / 2
    left = make_best_tree(lo, mid)
    right = make_best_tree(mid, hi)
    return (1, left, right)

def tree_get(tree, lo, hi, idx):
  (tag, left, right) = tree
  if hi - lo == 1:
    return left
  else:
    mid = (lo + hi) / 2
    if idx < mid:
      return tree_get(left, lo, mid, idx)
    else:
      return tree_get(right, mid, hi, idx)

def tree_set(tree, lo, hi, idx, value):
  (tag, left, right) = tree
  if hi - lo == 1:
    return (0, value, 0)
  else:
    mid = (lo + hi) / 2
    if idx < mid:
      left2 = tree_set(left, lo, mid, idx, value)
      return (1, left2, right)
    else:
      right2 = tree_set(right, mid, hi, idx, value)
      return (1, left, right2)

def find_root(dsu, size, node):
  entry = tree_get(dsu, 0, size, node)
  (parent, count) = entry
  if parent == node:
    return node
  else:
    return find_root(dsu, size, parent)

def update_best(best, size, root, u, v, w):
  old = tree_get(best, 0, size, root)
  (has, oldw, oldu, oldv) = old
  if has == 0:
    return tree_set(best, 0, size, root, (1, w, u, v))
  else:
    if w < oldw:
      return tree_set(best, 0, size, root, (1, w, u, v))
    else:
      return best

def scan_edges(edges, dsu, best, size):
  match edges:
    case List/Nil:
      return best
    case List/Cons:
      (u, v, w) = edges.head
      root_u = find_root(dsu, size, u)
      root_v = find_root(dsu, size, v)
      if root_u == root_v:
        return scan_edges(edges.tail, dsu, best, size)
      else:
        best1 = update_best(best, size, root_u, u, v, w)
        best2 = update_best(best1, size, root_v, u, v, w)
        return scan_edges(edges.tail, dsu, best2, size)

def apply_best(i, n, size, dsu, best, total, merges):
  if i == n:
    return (dsu, total, merges)
  else:
    candidate = tree_get(best, 0, size, i)
    (has, w, u, v) = candidate
    if has == 0:
      return apply_best(i + 1, n, size, dsu, best, total, merges)
    else:
      root_u = find_root(dsu, size, u)
      root_v = find_root(dsu, size, v)
      if root_u == root_v:
        return apply_best(i + 1, n, size, dsu, best, total, merges)
      else:
        entry_u = tree_get(dsu, 0, size, root_u)
        entry_v = tree_get(dsu, 0, size, root_v)
        (parent_u, count_u) = entry_u
        (parent_v, count_v) = entry_v
        if count_u < count_v:
          dsu1 = tree_set(dsu, 0, size, root_u, (root_v, count_u))
          dsu2 = tree_set(dsu1, 0, size, root_v, (root_v, count_u + count_v))
          return apply_best(i + 1, n, size, dsu2, best, total + w, merges + 1)
        else:
          dsu1 = tree_set(dsu, 0, size, root_v, (root_u, count_v))
          dsu2 = tree_set(dsu1, 0, size, root_u, (root_u, count_u + count_v))
          return apply_best(i + 1, n, size, dsu2, best, total + w, merges + 1)

def boruvka(n, edges, size, dsu, total):
  best0 = make_best_tree(0, size)
  best = scan_edges(edges, dsu, best0, size)
  (dsu2, total2, merges) = apply_best(0, n, size, dsu, best, total, 0)
  if merges == 0:
    return total2
  else:
    return boruvka(n, edges, size, dsu2, total2)
