def prog(x):
  (n, edges) = x
  return count_range(0, n, edges)

def scan_vertex(vertex, edges, incoming, outgoing):
  if incoming + outgoing == 2:
    return (0, 0)
  else:
    match edges:
      case List/Nil:
        return (1 - incoming, 1 - outgoing)
      case List/Cons:
        (u, v) = edges.head
        if v == vertex:
          return scan_vertex(vertex, edges.tail, 1, outgoing)
        else:
          if u == vertex:
            return scan_vertex(vertex, edges.tail, incoming, 1)
          else:
            return scan_vertex(vertex, edges.tail, incoming, outgoing)

def count_range(lo, hi, edges):
  if hi <= lo:
    return (0, 0)
  else:
    if hi - lo == 1:
      return scan_vertex(lo, edges, 0, 0)
    else:
      mid = lo + (hi - lo) / 2
      (left_sources, left_sinks) = count_range(lo, mid, edges)
      (right_sources, right_sinks) = count_range(mid, hi, edges)
      return (left_sources + right_sources, left_sinks + right_sinks)
