def prog(x):
  (n, s, b, edges) = x
  if s >= n:
    return 0
  else:
    ds = init_dist(n, s, 0)
    final_ds = dijkstra(ds, edges, b, n)
    return count_reachable(final_ds)

def init_dist(n, s, i):
  switch n:
    case 0:
      return []
    case _:
      if i == s:
        return List/Cons((1, 0), init_dist(n - 1, s, i + 1))
      else:
        return List/Cons((0, 0), init_dist(n - 1, s, i + 1))

def choose_min(ds, i, found, best_idx, best_dist):
  match ds:
    case List/Nil:
      return (found, best_idx, best_dist)
    case List/Cons:
      (state, distance) = ds.head
      if state == 1:
        if found == 0:
          return choose_min(ds.tail, i + 1, 1, i, distance)
        else:
          if distance < best_dist:
            return choose_min(ds.tail, i + 1, 1, i, distance)
          else:
            return choose_min(ds.tail, i + 1, found, best_idx, best_dist)
      else:
        return choose_min(ds.tail, i + 1, found, best_idx, best_dist)

def dist_at(ds, i):
  match ds:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      if i == 0:
        return ds.head
      else:
        return dist_at(ds.tail, i - 1)

def set_dist(ds, i, value):
  match ds:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, ds.tail)
      else:
        return List/Cons(ds.head, set_dist(ds.tail, i - 1, value))

def relax_target(ds, target, source_dist, weight, budget):
  if weight <= budget - source_dist:
    candidate = source_dist + weight
    (state, distance) = dist_at(ds, target)
    if state == 2:
      return ds
    else:
      if state == 0:
        return set_dist(ds, target, (1, candidate))
      else:
        if candidate < distance:
          return set_dist(ds, target, (1, candidate))
        else:
          return ds
  else:
    return ds

def relax_edges(edges, ds, source, source_dist, budget):
  match edges:
    case List/Nil:
      return ds
    case List/Cons:
      (u, v, weight) = edges.head
      if u == source:
        next_ds = relax_target(ds, v, source_dist, weight, budget)
      else:
        if v == source:
          next_ds = relax_target(ds, u, source_dist, weight, budget)
        else:
          next_ds = ds
      return relax_edges(edges.tail, next_ds, source, source_dist, budget)

def dijkstra(ds, edges, budget, rounds):
  switch rounds:
    case 0:
      return ds
    case _:
      (found, source, source_dist) = choose_min(ds, 0, 0, 0, 0)
      if found == 0:
        return ds
      else:
        settled_ds = set_dist(ds, source, (2, source_dist))
        next_ds = relax_edges(edges, settled_ds, source, source_dist, budget)
        return dijkstra(next_ds, edges, budget, rounds - 1)

def count_reachable(ds):
  match ds:
    case List/Nil:
      return 0
    case List/Cons:
      (state, distance) = ds.head
      rest = count_reachable(ds.tail)
      if state == 0:
        return rest
      else:
        return rest + 1
