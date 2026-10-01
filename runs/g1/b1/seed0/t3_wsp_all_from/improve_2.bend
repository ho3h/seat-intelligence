def prog(x):
  (n, s, edges) = x
  if s >= n:
    return make_inf(n)
  else:
    span = find_capacity(n, 1)
    dist = make_dist_tree(span, 0, n, s)
    priority = make_priority_tree(span, 0, n, s)
    adjacency = make_empty_adjacency(span)
    adjacency = build_adjacency(edges, adjacency, span, n)
    result = dijkstra(n, span, n, adjacency, dist, priority)
    return tree_to_list(result, span, n, 0)

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

def make_priority_tree(span, base, n, s):
  if span == 1:
    if base < n:
      if base == s:
        return (0, base)
      else:
        return (16777215, base)
    else:
      return (16777215, base)
  else:
    half = span / 2
    left = make_priority_tree(half, base, n, s)
    right = make_priority_tree(half, base + half, n, s)
    (left_best, left_index) = priority_summary(left, half)
    (right_best, right_index) = priority_summary(right, half)
    if left_best <= right_best:
      return (left, right, left_best, left_index)
    else:
      return (left, right, right_best, right_index)

def priority_summary(tree, span):
  if span == 1:
    return tree
  else:
    (left, right, best, index) = tree
    return (best, index)

def priority_set(tree, span, index, value):
  if span == 1:
    (old_value, vertex) = tree
    return (value, vertex)
  else:
    (left, right, old_best, old_index) = tree
    half = span / 2
    if index < half:
      new_left = priority_set(left, half, index, value)
      new_right = right
    else:
      new_left = left
      new_right = priority_set(right, half, index - half, value)
    (left_best, left_index) = priority_summary(new_left, half)
    (right_best, right_index) = priority_summary(new_right, half)
    if left_best <= right_best:
      return (new_left, new_right, left_best, left_index)
    else:
      return (new_left, new_right, right_best, right_index)

def make_empty_adjacency(span):
  if span == 1:
    return []
  else:
    half = span / 2
    left = make_empty_adjacency(half)
    right = make_empty_adjacency(half)
    return (left, right)

def adjacency_get(tree, span, index):
  if span == 1:
    return tree
  else:
    (left, right) = tree
    half = span / 2
    if index < half:
      return adjacency_get(left, half, index)
    else:
      return adjacency_get(right, half, index - half)

def adjacency_set(tree, span, index, value):
  if span == 1:
    return value
  else:
    (left, right) = tree
    half = span / 2
    if index < half:
      return (adjacency_set(left, half, index, value), right)
    else:
      return (left, adjacency_set(right, half, index - half, value))

def build_adjacency(edges, adjacency, span, n):
  match edges:
    case List/Nil:
      return adjacency
    case List/Cons:
      (src, dst, weight) = edges.head
      if src < n and dst < n:
        bucket = adjacency_get(adjacency, span, src)
        new_bucket = List/Cons((dst, weight), bucket)
        new_adjacency = adjacency_set(adjacency, span, src, new_bucket)
      else:
        new_adjacency = adjacency
      return build_adjacency(edges.tail, new_adjacency, span, n)

def dist_get(tree, span, index):
  if span == 1:
    return tree
  else:
    (left, right) = tree
    half = span / 2
    if index < half:
      return dist_get(left, half, index)
    else:
      return dist_get(right, half, index - half)

def dist_set(tree, span, index, value):
  if span == 1:
    return value
  else:
    (left, right) = tree
    half = span / 2
    if index < half:
      return (dist_set(left, half, index, value), right)
    else:
      return (left, dist_set(right, half, index - half, value))

def relax_bucket(bucket, dist, priority, span, n, du):
  match bucket:
    case List/Nil:
      return (dist, priority)
    case List/Cons:
      (dst, weight) = bucket.head
      if weight > 16777215 - du:
        new_dist = dist
        new_priority = priority
      else:
        candidate = du + weight
        old = dist_get(dist, span, dst)
        if candidate < old:
          new_dist = dist_set(dist, span, dst, candidate)
          new_priority = priority_set(priority, span, dst, candidate)
        else:
          new_dist = dist
          new_priority = priority
      return relax_bucket(bucket.tail, new_dist, new_priority, span, n, du)

def dijkstra(k, span, n, adjacency, dist, priority):
  switch k:
    case 0:
      return dist
    case _:
      (best, vertex) = priority_summary(priority, span)
      if best == 16777215:
        return dist
      else:
        bucket = adjacency_get(adjacency, span, vertex)
        marked_priority = priority_set(priority, span, vertex, 16777215)
        (new_dist, new_priority) = relax_bucket(bucket, dist, marked_priority, span, n, best)
        return dijkstra(k - 1, span, n, adjacency, new_dist, new_priority)

def tree_to_list(tree, span, n, index):
  switch n:
    case 0:
      return []
    case _:
      value = dist_get(tree, span, index)
      return List/Cons(value, tree_to_list(tree, span, n - 1, index + 1))
