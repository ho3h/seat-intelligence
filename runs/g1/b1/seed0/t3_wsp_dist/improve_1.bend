def dist_get(ds, i):
  match ds:
    case List/Nil:
      return (16777215, 1)
    case List/Cons:
      switch i:
        case 0:
          return ds.head
        case _:
          return dist_get(ds.tail, i - 1)

def dist_set(ds, i, value):
  match ds:
    case List/Nil:
      return []
    case List/Cons:
      switch i:
        case 0:
          return List/Cons(value, ds.tail)
        case _:
          return List/Cons(ds.head, dist_set(ds.tail, i - 1, value))

def make_dist(n, s, i):
  switch n:
    case 0:
      return []
    case _:
      tail = make_dist(n - 1, s, i + 1)
      if i == s:
        return List/Cons((0, 0), tail)
      else:
        return List/Cons((16777215, 0), tail)

def find_min(ds, i, best_idx, best_dist):
  match ds:
    case List/Nil:
      return (best_idx, best_dist)
    case List/Cons:
      (d, visited) = ds.head
      if visited == 0:
        if d < best_dist:
          return find_min(ds.tail, i + 1, i, d)
        else:
          return find_min(ds.tail, i + 1, best_idx, best_dist)
      else:
        return find_min(ds.tail, i + 1, best_idx, best_dist)

def relax_to(ds, dst, src_dist, w, n):
  if dst >= n:
    return ds
  else:
    if w >= 16777215 - src_dist:
      return ds
    else:
      (dst_dist, visited) = dist_get(ds, dst)
      if visited == 1:
        return ds
      else:
        candidate = src_dist + w
        if candidate < dst_dist:
          return dist_set(ds, dst, (candidate, 0))
        else:
          return ds

def scan_edges(edges, ds, src, src_dist, n):
  match edges:
    case List/Nil:
      return ds
    case List/Cons:
      (u, v, w) = edges.head
      if u == src:
        ds1 = relax_to(ds, v, src_dist, w, n)
      else:
        ds1 = ds
      if v == src:
        ds2 = relax_to(ds1, u, src_dist, w, n)
      else:
        ds2 = ds1
      return scan_edges(edges.tail, ds2, src, src_dist, n)

def dijkstra(ds, edges, remaining, n, t):
  switch remaining:
    case 0:
      (answer, visited) = dist_get(ds, t)
      return answer
    case _:
      (src, best_dist) = find_min(ds, 0, 0, 16777215)
      if best_dist == 16777215:
        return 16777215
      else:
        if src == t:
          return best_dist
        else:
          ds1 = dist_set(ds, src, (best_dist, 1))
          ds2 = scan_edges(edges, ds1, src, best_dist, n)
          return dijkstra(ds2, edges, remaining - 1, n, t)

def prog(x):
  (n, s, t, edges) = x
  if s >= n:
    return 16777215
  else:
    if t >= n:
      return 16777215
    else:
      if s == t:
        return 0
      else:
        ds = make_dist(n, s, 0)
        return dijkstra(ds, edges, n, n, t)
