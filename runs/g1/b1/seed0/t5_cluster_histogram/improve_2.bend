def prog(x):
  (n, pairs) = x
  parent = build_parent(0, n)
  sizes = build_sizes(0, n)
  (parent2, sizes2) = union_all(pairs, parent, sizes, n)
  return count_roots(parent2, sizes2, 0, n, [0, 0, 0, 0, 0, 0, 0, 0])

def build_parent(lo, hi):
  if lo == hi:
    return 0
  else:
    if lo + 1 == hi:
      return lo
    else:
      mid = (lo + hi) / 2
      return (build_parent(lo, mid), build_parent(mid, hi))

def build_sizes(lo, hi):
  if lo == hi:
    return 0
  else:
    if lo + 1 == hi:
      return 1
    else:
      mid = (lo + hi) / 2
      return (build_sizes(lo, mid), build_sizes(mid, hi))

def tree_get(tree, lo, hi, i):
  if lo + 1 == hi:
    return tree
  else:
    mid = (lo + hi) / 2
    (left, right) = tree
    if i < mid:
      return tree_get(left, lo, mid, i)
    else:
      return tree_get(right, mid, hi, i)

def tree_set(tree, lo, hi, i, value):
  if lo + 1 == hi:
    return value
  else:
    mid = (lo + hi) / 2
    (left, right) = tree
    if i < mid:
      return (tree_set(left, lo, mid, i, value), right)
    else:
      return (left, tree_set(right, mid, hi, i, value))

def find_compress(parent, node, n):
  p = tree_get(parent, 0, n, node)
  if p == node:
    return (node, parent)
  else:
    (root, parent2) = find_compress(parent, p, n)
    if p == root:
      return (root, parent2)
    else:
      return (root, tree_set(parent2, 0, n, node, root))

def union_all(edges, parent, sizes, n):
  match edges:
    case List/Nil:
      return (parent, sizes)
    case List/Cons:
      (u, v) = edges.head
      (root_u, parent1) = find_compress(parent, u, n)
      (root_v, parent2) = find_compress(parent1, v, n)
      if root_u == root_v:
        return union_all(edges.tail, parent2, sizes, n)
      else:
        size_u = tree_get(sizes, 0, n, root_u)
        size_v = tree_get(sizes, 0, n, root_v)
        if size_u < size_v:
          parent3 = tree_set(parent2, 0, n, root_u, root_v)
          sizes2 = tree_set(sizes, 0, n, root_v, size_u + size_v)
          return union_all(edges.tail, parent3, sizes2, n)
        else:
          parent3 = tree_set(parent2, 0, n, root_v, root_u)
          sizes2 = tree_set(sizes, 0, n, root_u, size_u + size_v)
          return union_all(edges.tail, parent3, sizes2, n)

def increment_at(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(xs.head + 1, xs.tail)
      else:
        return List/Cons(xs.head, increment_at(xs.tail, i - 1))

def count_roots(parent, sizes, i, n, hist):
  if i == n:
    return hist
  else:
    p = tree_get(parent, 0, n, i)
    if p == i:
      component_size = tree_get(sizes, 0, n, i)
      if component_size >= 8:
        bin = 7
      else:
        bin = component_size - 1
      hist2 = increment_at(hist, bin)
      return count_roots(parent, sizes, i + 1, n, hist2)
    else:
      return count_roots(parent, sizes, i + 1, n, hist)
