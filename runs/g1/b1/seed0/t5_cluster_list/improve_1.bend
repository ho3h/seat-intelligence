def prog(x):
  (n, pairs) = x
  if n == 0:
    return []
  else:
    size = next_power(1, n)
    parents = build_identity(0, size)
    sizes = build_sizes(0, size, n)
    mins = parents
    (parents2, sizes2, mins2) = merge_edges(pairs, parents, sizes, mins, size)
    (roots, parents3) = collect_roots(0, n, parents2, size)
    return build_output(roots, roots, 0, mins2, size)

def next_power(p, n):
  if p >= n:
    return p
  else:
    return next_power(p * 2, n)

def build_identity(lo, hi):
  if hi - lo == 1:
    return (0, lo, 0)
  else:
    mid = (lo + hi) / 2
    left = build_identity(lo, mid)
    right = build_identity(mid, hi)
    return (1, left, right)

def build_sizes(lo, hi, n):
  if hi - lo == 1:
    if lo < n:
      return (0, 1, 0)
    else:
      return (0, 0, 0)
  else:
    mid = (lo + hi) / 2
    left = build_sizes(lo, mid, n)
    right = build_sizes(mid, hi, n)
    return (1, left, right)

def tree_get(tree, idx, lo, hi):
  (tag, a, b) = tree
  if tag == 0:
    return a
  else:
    mid = (lo + hi) / 2
    if idx < mid:
      return tree_get(a, idx, lo, mid)
    else:
      return tree_get(b, idx, mid, hi)

def tree_set(tree, idx, value, lo, hi):
  (tag, a, b) = tree
  if tag == 0:
    return (0, value, 0)
  else:
    mid = (lo + hi) / 2
    if idx < mid:
      left = tree_set(a, idx, value, lo, mid)
      return (1, left, b)
    else:
      right = tree_set(b, idx, value, mid, hi)
      return (1, a, right)

def find_root(parents, x, size):
  p = tree_get(parents, x, 0, size)
  if p == x:
    return (x, parents)
  else:
    (root, parents2) = find_root(parents, p, size)
    parents3 = tree_set(parents2, x, root, 0, size)
    return (root, parents3)

def merge_edges(edges, parents, sizes, mins, size):
  match edges:
    case List/Nil:
      return (parents, sizes, mins)
    case List/Cons:
      (u, v) = edges.head
      (ru, parents1) = find_root(parents, u, size)
      (rv, parents2) = find_root(parents1, v, size)
      if ru == rv:
        return merge_edges(edges.tail, parents2, sizes, mins, size)
      else:
        su = tree_get(sizes, ru, 0, size)
        sv = tree_get(sizes, rv, 0, size)
        min_u = tree_get(mins, ru, 0, size)
        min_v = tree_get(mins, rv, 0, size)
        if su >= sv:
          parents3 = tree_set(parents2, rv, ru, 0, size)
          sizes2 = tree_set(sizes, ru, su + sv, 0, size)
          if min_u < min_v:
            mins2 = tree_set(mins, ru, min_u, 0, size)
          else:
            mins2 = tree_set(mins, ru, min_v, 0, size)
          return merge_edges(edges.tail, parents3, sizes2, mins2, size)
        else:
          parents3 = tree_set(parents2, ru, rv, 0, size)
          sizes2 = tree_set(sizes, rv, su + sv, 0, size)
          if min_u < min_v:
            mins2 = tree_set(mins, rv, min_u, 0, size)
          else:
            mins2 = tree_set(mins, rv, min_v, 0, size)
          return merge_edges(edges.tail, parents3, sizes2, mins2, size)

def collect_roots(i, n, parents, size):
  if i == n:
    return ([], parents)
  else:
    (root, parents1) = find_root(parents, i, size)
    (tail, parents2) = collect_roots(i + 1, n, parents1, size)
    return (List/Cons(root, tail), parents2)

def collect_members(roots, i, target):
  match roots:
    case List/Nil:
      return []
    case List/Cons:
      tail = collect_members(roots.tail, i + 1, target)
      if roots.head == target:
        return List/Cons(i, tail)
      else:
        return tail

def build_output(rest, all_roots, i, mins, size):
  match rest:
    case List/Nil:
      return []
    case List/Cons:
      tail = build_output(rest.tail, all_roots, i + 1, mins, size)
      root_min = tree_get(mins, rest.head, 0, size)
      if root_min == i:
        group = collect_members(all_roots, 0, rest.head)
        return List/Cons(group, tail)
      else:
        return tail
