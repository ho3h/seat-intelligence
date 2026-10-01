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

def adj_get(adj, i):
  match adj:
    case List/Nil:
      return []
    case List/Cons:
      switch i:
        case 0:
          return adj.head
        case _:
          return adj_get(adj.tail, i - 1)

def adj_set(adj, i, value):
  match adj:
    case List/Nil:
      return []
    case List/Cons:
      switch i:
        case 0:
          return List/Cons(value, adj.tail)
        case _:
          return List/Cons(adj.head, adj_set(adj.tail, i - 1, value))

def make_adjs(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons([], make_adjs(n - 1))

def add_edge_to_adj(adj, src, dst, w):
  neighbors = adj_get(adj, src)
  return adj_set(adj, src, List/Cons((dst, w), neighbors))

def build_adjs(edges, adj, n):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v, w) = edges.head
      if u < n:
        if v < n:
          adj1 = add_edge_to_adj(adj, u, v, w)
          adj2 = add_edge_to_adj(adj1, v, u, w)
          return build_adjs(edges.tail, adj2, n)
        else:
          return build_adjs(edges.tail, adj, n)
      else:
        return build_adjs(edges.tail, adj, n)

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

def relax_neighbor(ds, dst, src_dist, w, n):
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

def relax_neighbors(neighbors, ds, src_dist, n):
  match neighbors:
    case List/Nil:
      return ds
    case List/Cons:
      (dst, w) = neighbors.head
      ds1 = relax_neighbor(ds, dst, src_dist, w, n)
      return relax_neighbors(neighbors.tail, ds1, src_dist, n)

def dijkstra(ds, adj, remaining, n, t):
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
          neighbors = adj_get(adj, src)
          ds2 = relax_neighbors(neighbors, ds1, best_dist, n)
          return dijkstra(ds2, adj, remaining - 1, n, t)

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
        adj0 = make_adjs(n)
        adj = build_adjs(edges, adj0, n)
        ds = make_dist(n, s, 0)
        return dijkstra(ds, adj, n, n, t)
