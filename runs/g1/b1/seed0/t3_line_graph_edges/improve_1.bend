def prog(x):
  (n, edges) = x
  m = list_length(edges)
  if n <= m:
    return sum_vertex_range(edges, 0, n)
  else:
    return count_pairs(edges)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def sum_vertex_range(edges, lo, hi):
  if lo == hi:
    return 0
  else:
    size = hi - lo
    if size == 1:
      degree = vertex_degree(edges, lo)
      if degree < 2:
        return 0
      else:
        if degree % 2 == 0:
          return (degree / 2) * (degree - 1)
        else:
          return degree * ((degree - 1) / 2)
    else:
      mid = lo + (size / 2)
      left = sum_vertex_range(edges, lo, mid)
      right = sum_vertex_range(edges, mid, hi)
      return left + right

def vertex_degree(edges, vertex):
  match edges:
    case List/Nil:
      return 0
    case List/Cons:
      (u, v) = edges.head
      if u == vertex:
        return 1 + vertex_degree(edges.tail, vertex)
      else:
        if v == vertex:
          return 1 + vertex_degree(edges.tail, vertex)
        else:
          return vertex_degree(edges.tail, vertex)

def count_pairs(edges):
  match edges:
    case List/Nil:
      return 0
    case List/Cons:
      shared = count_shared(edges.head, edges.tail)
      rest = count_pairs(edges.tail)
      return shared + rest

def count_shared(edge, edges):
  match edges:
    case List/Nil:
      return 0
    case List/Cons:
      (u, v) = edge
      (a, b) = edges.head
      if (u == a) | (u == b) | (v == a) | (v == b):
        return 1 + count_shared(edge, edges.tail)
      else:
        return count_shared(edge, edges.tail)
