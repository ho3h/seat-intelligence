def prog(x):
  (n, s, b, edges) = x
  if s >= n:
    return 0
  else:
    ds = init_dist(n, s, 0)
    final_ds = relax_rounds(ds, edges, b, n)
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

def dist_at(xs, i):
  match xs:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return dist_at(xs.tail, i - 1)

def set_dist(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_dist(xs.tail, i - 1, value))

def relax(ds, target, source_reachable, source_dist, weight, budget):
  if source_reachable == 1:
    if weight <= budget - source_dist:
      candidate = source_dist + weight
      (target_reachable, target_dist) = dist_at(ds, target)
      if target_reachable == 0:
        return (set_dist(ds, target, (1, candidate)), 1)
      else:
        if candidate < target_dist:
          return (set_dist(ds, target, (1, candidate)), 1)
        else:
          return (ds, 0)
    else:
      return (ds, 0)
  else:
    return (ds, 0)

def relax_edges(edges, ds, budget, changed):
  match edges:
    case List/Nil:
      return (ds, changed)
    case List/Cons:
      (u, v, weight) = edges.head
      (u_reachable, u_dist) = dist_at(ds, u)
      (v_reachable, v_dist) = dist_at(ds, v)
      (ds1, changed1) = relax(ds, v, u_reachable, u_dist, weight, budget)
      (ds2, changed2) = relax(ds1, u, v_reachable, v_dist, weight, budget)
      return relax_edges(edges.tail, ds2, budget, changed | changed1 | changed2)

def relax_rounds(ds, edges, budget, rounds):
  switch rounds:
    case 0:
      return ds
    case _:
      (next_ds, changed) = relax_edges(edges, ds, budget, 0)
      if changed == 0:
        return next_ds
      else:
        return relax_rounds(next_ds, edges, budget, rounds - 1)

def count_reachable(ds):
  match ds:
    case List/Nil:
      return 0
    case List/Cons:
      (reachable, distance) = ds.head
      rest = count_reachable(ds.tail)
      if reachable == 1:
        return rest + 1
      else:
        return rest
