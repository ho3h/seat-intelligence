def prog(x):
  (n, edges) = x
  if n == 0:
    return 16777215
  else:
    d = vertex_degree(edges, 0)
    return best_vertex(n, edges, 1, 0, d)

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

def best_vertex(n, edges, i, best_v, best_d):
  if i == n:
    return best_v
  else:
    d = vertex_degree(edges, i)
    if d > best_d:
      return best_vertex(n, edges, i + 1, i, d)
    else:
      return best_vertex(n, edges, i + 1, best_v, best_d)
