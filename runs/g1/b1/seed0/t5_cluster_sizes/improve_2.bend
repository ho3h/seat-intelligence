def prog(x):
  (n, edges) = x
  if n == 0:
    return []
  else:
    span = find_span(1, n)
    (parents, sizes) = make_trees(0, span, n)
    (parents, sizes) = process_edges(edges, parents, sizes, span)
    roots = make_roots(0, n, parents, span)
    return collect_sizes(roots, roots, 0)

def find_span(span, n):
  if span < n:
    return find_span(span * 2, n)
  else:
    return span

def make_trees(lo, hi, n):
  if hi - lo == 1:
    if lo < n:
      return (lo, 1)
    else:
      return (lo, 0)
  else:
    mid = lo + (hi - lo) / 2
    (left_parents, left_sizes) = make_trees(lo, mid, n)
    (right_parents, right_sizes) = make_trees(mid, hi, n)
    return (
      (left_parents, right_parents),
      (left_sizes, right_sizes)
    )

def tree_get(tree, lo, span, index):
  if span == 1:
    return tree
  else:
    (left, right) = tree
    half = span / 2
    if index < lo + half:
      return tree_get(left, lo, half, index)
    else:
      return tree_get(right, lo + half, half, index)

def tree_set(tree, lo, span, index, value):
  if span == 1:
    return value
  else:
    (left, right) = tree
    half = span / 2
    if index < lo + half:
      return (
        tree_set(left, lo, half, index, value),
        right
      )
    else:
      return (
        left,
        tree_set(right, lo + half, half, index, value)
      )

def find_root(parents, span, index):
  parent = tree_get(parents, 0, span, index)
  if parent == index:
    return index
  else:
    return find_root(parents, span, parent)

def process_edges(edges, parents, sizes, span):
  match edges:
    case List/Nil:
      return (parents, sizes)
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(parents, span, u)
      root_v = find_root(parents, span, v)
      if root_u == root_v:
        return process_edges(edges.tail, parents, sizes, span)
      else:
        size_u = tree_get(sizes, 0, span, root_u)
        size_v = tree_get(sizes, 0, span, root_v)
        if size_u < size_v:
          total = size_u + size_v
          new_parents = tree_set(parents, 0, span, root_u, root_v)
          new_sizes = tree_set(sizes, 0, span, root_v, total)
          return process_edges(edges.tail, new_parents, new_sizes, span)
        else:
          if size_v < size_u:
            total = size_u + size_v
            new_parents = tree_set(parents, 0, span, root_v, root_u)
            new_sizes = tree_set(sizes, 0, span, root_u, total)
            return process_edges(edges.tail, new_parents, new_sizes, span)
          else:
            total = size_u + size_v
            if root_u < root_v:
              new_parents = tree_set(parents, 0, span, root_v, root_u)
              new_sizes = tree_set(sizes, 0, span, root_u, total)
              return process_edges(edges.tail, new_parents, new_sizes, span)
            else:
              new_parents = tree_set(parents, 0, span, root_u, root_v)
              new_sizes = tree_set(sizes, 0, span, root_v, total)
              return process_edges(edges.tail, new_parents, new_sizes, span)

def make_roots(i, n, parents, span):
  if i == n:
    return []
  else:
    root = find_root(parents, span, i)
    return List/Cons(root, make_roots(i + 1, n, parents, span))

def count_and_max(roots, target, i, count, largest):
  match roots:
    case List/Nil:
      return (count, largest)
    case List/Cons:
      if roots.head == target:
        return count_and_max(roots.tail, target, i + 1, count + 1, i)
      else:
        return count_and_max(roots.tail, target, i + 1, count, largest)

def collect_sizes(roots, all_roots, i):
  match roots:
    case List/Nil:
      return []
    case List/Cons:
      (size, largest) = count_and_max(all_roots, roots.head, 0, 0, 0)
      rest = collect_sizes(roots.tail, all_roots, i + 1)
      if largest == i:
        return List/Cons(size, rest)
      else:
        return rest
