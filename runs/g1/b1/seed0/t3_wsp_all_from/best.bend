def prog(x):
  (n, s, edges) = x
  if s >= n:
    return make_inf(n)
  else:
    span = find_capacity(n, 1)
    dist = make_dist_tree(span, 0, n, s)
    seen = make_zero_tree(span)
    final_dist = dijkstra(n, span, n, edges, dist, seen)
    return tree_to_list(final_dist, span, n, 0)

def make_inf(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(16777215, make_inf(n - 1))

def find_capacity(n, cap):
  if cap >= n:
    return cap
  else:
    return find_capacity(n, cap * 2)

def make_dist_tree(span, base, n, s):
  if span == 1:
    if base < n:
      if base == s:
        return 0
      else:
        return 16777215
    else:
      return 16777215
  else:
    half = span / 2
    left = make_dist_tree(half, base, n, s)
    right = make_dist_tree(half, base + half, n, s)
    return (left, right)

def make_zero_tree(span):
  if span == 1:
    return 0
  else:
    half = span / 2
    left = make_zero_tree(half)
    right = make_zero_tree(half)
    return (left, right)

def get_tree(tree, span, index):
  if span == 1:
    return tree
  else:
    (left, right) = tree
    half = span / 2
    if index < half:
      return get_tree(left, half, index)
    else:
      return get_tree(right, half, index - half)

def set_tree(tree, span, index, value):
  if span == 1:
    return value
  else:
    (left, right) = tree
    half = span / 2
    if index < half:
      return (set_tree(left, half, index, value), right)
    else:
      return (left, set_tree(right, half, index - half, value))

def find_min(dist, seen, span, base, n):
  if span == 1:
    if base < n:
      if seen == 0:
        return (dist, base)
      else:
        return (16777215, 0)
    else:
      return (16777215, 0)
  else:
    (dl, dr) = dist
    (sl, sr) = seen
    half = span / 2
    (left_min, left_index) = find_min(dl, sl, half, base, n)
    (right_min, right_index) = find_min(dr, sr, half, base + half, n)
    if left_min <= right_min:
      return (left_min, left_index)
    else:
      return (right_min, right_index)

def relax_edges(edges, dist, seen, span, n, u, du):
  match edges:
    case List/Nil:
      return dist
    case List/Cons:
      (from, to, weight) = edges.head
      if from == u:
        if to >= n:
          updated = dist
        else:
          was_seen = get_tree(seen, span, to)
          if was_seen != 0:
            updated = dist
          else:
            if weight > 16777215 - du:
              updated = dist
            else:
              candidate = du + weight
              old = get_tree(dist, span, to)
              if candidate < old:
                updated = set_tree(dist, span, to, candidate)
              else:
                updated = dist
      else:
        updated = dist
      return relax_edges(edges.tail, updated, seen, span, n, u, du)

def dijkstra(k, span, n, edges, dist, seen):
  switch k:
    case 0:
      return dist
    case _:
      (best, u) = find_min(dist, seen, span, 0, n)
      if best == 16777215:
        return dist
      else:
        marked = set_tree(seen, span, u, 1)
        updated = relax_edges(edges, dist, marked, span, n, u, best)
        return dijkstra(k - 1, span, n, edges, updated, marked)

def tree_to_list(tree, span, n, index):
  switch n:
    case 0:
      return []
    case _:
      value = get_tree(tree, span, index)
      return List/Cons(value, tree_to_list(tree, span, n - 1, index + 1))
