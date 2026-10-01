def prog(x):
  (n, edges) = x
  size = tree_size(n, 1)
  labels = make_label_tree(0, size, n)
  return boruvka(n, edges, size, labels, 0)

def tree_size(n, p):
  if p >= n:
    return p
  else:
    return tree_size(n, p * 2)

def make_label_tree(lo, hi, n):
  if hi - lo == 1:
    if lo < n:
      return (0, lo, 0)
    else:
      return (0, 0, 0)
  else:
    mid = (lo + hi) / 2
    left = make_label_tree(lo, mid, n)
    right = make_label_tree(mid, hi, n)
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

def scan_edges(edges, labels, best, size):
  match edges:
    case List/Nil:
      return best
    case List/Cons:
      (u, v, w) = edges.head
      root_u = tree_get(labels, 0, size, u)
      root_v = tree_get(labels, 0, size, v)
      if root_u == root_v:
        return scan_edges(edges.tail, labels, best, size)
      else:
        best1 = update_best(best, size, root_u, u, v, w)
        best2 = update_best(best1, size, root_v, u, v, w)
        return scan_edges(edges.tail, labels, best2, size)

def relabel(tree, lo, hi, n, old, new):
  if lo >= n:
    return tree
  else:
    (tag, left, right) = tree
    if hi - lo == 1:
      if left == old:
        return (0, new, 0)
      else:
        return tree
    else:
      mid = (lo + hi) / 2
      left2 = relabel(left, lo, mid, n, old, new)
      right2 = relabel(right, mid, hi, n, old, new)
      return (1, left2, right2)

def apply_best(i, n, size, labels, best, total, merges):
  if i == n:
    return (labels, total, merges)
  else:
    candidate = tree_get(best, 0, size, i)
    (has, w, u, v) = candidate
    if has == 0:
      return apply_best(i + 1, n, size, labels, best, total, merges)
    else:
      root_u = tree_get(labels, 0, size, u)
      root_v = tree_get(labels, 0, size, v)
      if root_u == root_v:
        return apply_best(i + 1, n, size, labels, best, total, merges)
      else:
        labels2 = relabel(labels, 0, size, n, root_u, root_v)
        return apply_best(i + 1, n, size, labels2, best, total + w, merges + 1)

def boruvka(n, edges, size, labels, total):
  best0 = make_best_tree(0, size)
  best = scan_edges(edges, labels, best0, size)
  (labels2, total2, merges) = apply_best(0, n, size, labels, best, 0, total)
  if merges == 0:
    return total2
  else:
    return boruvka(n, edges, size, labels2, total2)
