def dist_get(ds, i):
  match ds:
    case List/Nil:
      return 16777215
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
        return List/Cons(0, tail)
      else:
        return List/Cons(16777215, tail)

def relax_dir(ds, src, dst, w):
  src_dist = dist_get(ds, src)
  if src_dist == 16777215:
    return ds
  else:
    if w >= 16777215 - src_dist:
      return ds
    else:
      candidate = src_dist + w
      dst_dist = dist_get(ds, dst)
      if candidate < dst_dist:
        return dist_set(ds, dst, candidate)
      else:
        return ds

def scan_edges(edges, ds, n):
  match edges:
    case List/Nil:
      return ds
    case List/Cons:
      (u, v, w) = edges.head
      if u < n:
        if v < n:
          ds1 = relax_dir(ds, u, v, w)
          ds2 = relax_dir(ds1, v, u, w)
          return scan_edges(edges.tail, ds2, n)
        else:
          return scan_edges(edges.tail, ds, n)
      else:
        return scan_edges(edges.tail, ds, n)

def run_rounds(ds, edges, rounds, n):
  switch rounds:
    case 0:
      return ds
    case _:
      ds1 = scan_edges(edges, ds, n)
      return run_rounds(ds1, edges, rounds - 1, n)

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
        final_ds = run_rounds(ds, edges, n, n)
        return dist_get(final_ds, t)
