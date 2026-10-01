def prog(x):
  (n, s, budget, edges) = x
  if s >= n:
    return 0
  else:
    cap = next_capacity(n, 1)
    adj = make_adj(cap)
    full_adj = build_adjacency(edges, adj, cap)
    distances = make_dist(cap, 0, n, s)
    return dijkstra(distances, full_adj, cap, budget, n, 0)

def next_capacity(n, cap):
  if cap >= n:
    return cap
  else:
    return next_capacity(n, cap * 2)

def make_adj(size):
  if size == 1:
    return (0, [], 0, 0)
  else:
    half = size / 2
    left = make_adj(half)
    right = make_adj(half)
    return (1, 0, left, right)

def adj_get(tree, index, size):
  if size == 1:
    (kind, value, left, right) = tree
    return value
  else:
    (kind, value, left, right) = tree
    half = size / 2
    if index < half:
      return adj_get(left, index, half)
    else:
      return adj_get(right, index - half, half)

def adj_set(tree, index, size, new_value):
  if size == 1:
    return (0, new_value, 0, 0)
  else:
    (kind, value, left, right) = tree
    half = size / 2
    if index < half:
      new_left = adj_set(left, index, half, new_value)
      return (1, 0, new_left, right)
    else:
      new_right = adj_set(right, index - half, half, new_value)
      return (1, 0, left, new_right)

def add_neighbor(adj, source, target, weight, cap):
  neighbors = adj_get(adj, source, cap)
  return adj_set(adj, source, cap, List/Cons((target, weight), neighbors))

def build_adjacency(edges, adj, cap):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v, weight) = edges.head
      adj1 = add_neighbor(adj, u, v, weight, cap)
      adj2 = add_neighbor(adj1, v, u, weight, cap)
      return build_adjacency(edges.tail, adj2, cap)

def make_dist(size, base, n, source):
  if size == 1:
    if base == source:
      return (0, 1, 0, base, 0, 0)
    else:
      return (0, 0, 0, base, 0, 0)
  else:
    half = size / 2
    left = make_dist(half, base, n, source)
    right = make_dist(half, base + half, n, source)
    return merge_dist(left, right)

def merge_dist(left, right):
  (lk, ls, ld, li, ll, lr) = left
  (rk, rs, rd, ri, rl, rr) = right
  if ls == 1:
    if rs == 1:
      if ld <= rd:
        return (1, 1, ld, li, left, right)
      else:
        return (1, 1, rd, ri, left, right)
    else:
      return (1, 1, ld, li, left, right)
  else:
    if rs == 1:
      return (1, 1, rd, ri, left, right)
    else:
      return (1, 0, 0, 0, left, right)

def dist_lookup(tree, index, size):
  if size == 1:
    (kind, state, distance, vertex, left, right) = tree
    return (state, distance)
  else:
    (kind, state, distance, vertex, left, right) = tree
    half = size / 2
    if index < half:
      return dist_lookup(left, index, half)
    else:
      return dist_lookup(right, index - half, half)

def dist_update(tree, index, base, size, new_state, new_distance):
  if size == 1:
    return (0, new_state, new_distance, base, 0, 0)
  else:
    (kind, state, distance, vertex, left, right) = tree
    half = size / 2
    if index < half:
      new_left = dist_update(left, index, base, half, new_state, new_distance)
      return merge_dist(new_left, right)
    else:
      new_right = dist_update(right, index - half, base + half, half, new_state, new_distance)
      return merge_dist(left, new_right)

def relax_neighbors(neighbors, distances, cap, source_distance, budget):
  match neighbors:
    case List/Nil:
      return distances
    case List/Cons:
      (target, weight) = neighbors.head
      if weight <= budget - source_distance:
        candidate = source_distance + weight
        (state, old_distance) = dist_lookup(distances, target, cap)
        if state == 2:
          next_distances = distances
        else:
          if state == 0:
            next_distances = dist_update(distances, target, 0, cap, 1, candidate)
          else:
            if candidate < old_distance:
              next_distances = dist_update(distances, target, 0, cap, 1, candidate)
            else:
              next_distances = distances
      else:
        next_distances = distances
      return relax_neighbors(neighbors.tail, next_distances, cap, source_distance, budget)

def dijkstra(distances, adj, cap, budget, rounds, count):
  switch rounds:
    case 0:
      return count
    case _:
      (kind, state, distance, vertex, left, right) = distances
      if state == 0:
        return count
      else:
        settled = dist_update(distances, vertex, 0, cap, 2, distance)
        neighbors = adj_get(adj, vertex, cap)
        next_distances = relax_neighbors(neighbors, settled, cap, distance, budget)
        return dijkstra(next_distances, adj, cap, budget, rounds - 1, count + 1)
