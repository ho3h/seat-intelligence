def prog(x):
  (n, edges) = x
  if n == 0:
    return 16777215
  else:
    (v, d) = best_range(edges, 0, n)
    return v

def vertex_degree(edges, vertex):
  match edges:
    case List/Nil:
      return 0
    case List/Cons:
      (u, v) = edges.head
      d = vertex_degree(edges.tail, vertex)
      if u == vertex:
        if v == vertex:
          return d + 2
        else:
          return d + 1
      else:
        if v == vertex:
          return d + 1
        else:
          return d

def best_range(edges, lo, hi):
  if hi - lo == 1:
    d = vertex_degree(edges, lo)
    return (lo, d)
  else:
    mid = lo + (hi - lo) / 2
    (left_v, left_d) = best_range(edges, lo, mid)
    (right_v, right_d) = best_range(edges, mid, hi)
    if left_d >= right_d:
      return (left_v, left_d)
    else:
      return (right_v, right_d)
