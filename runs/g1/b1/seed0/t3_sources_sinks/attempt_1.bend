def prog(x):
  (n, edges) = x
  return count_vertices(n, 0, edges, 0, 0)

def has_in(vertex, edges):
  match edges:
    case List/Nil:
      return 0
    case List/Cons:
      (u, v) = edges.head
      if v == vertex:
        return 1
      else:
        return has_in(vertex, edges.tail)

def has_out(vertex, edges):
  match edges:
    case List/Nil:
      return 0
    case List/Cons:
      (u, v) = edges.head
      if u == vertex:
        return 1
      else:
        return has_out(vertex, edges.tail)

def count_vertices(n, i, edges, sources, sinks):
  if i == n:
    return (sources, sinks)
  else:
    incoming = has_in(i, edges)
    outgoing = has_out(i, edges)
    return count_vertices(n, i + 1, edges, sources + 1 - incoming, sinks + 1 - outgoing)
