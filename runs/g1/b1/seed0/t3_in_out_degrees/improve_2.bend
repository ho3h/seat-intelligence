def prog(x):
  (n, edges) = x
  return build_degrees(n, edges, 0)

def build_degrees(n, edges, vertex):
  if vertex == n:
    return ([], [])
  else:
    (in_count, out_count) = degree_at(edges, vertex, 0, 0)
    (ins, outs) = build_degrees(n, edges, vertex + 1)
    return (List/Cons(in_count, ins), List/Cons(out_count, outs))

def degree_at(edges, vertex, in_count, out_count):
  match edges:
    case List/Nil:
      return (in_count, out_count)
    case List/Cons:
      (u, v) = edges.head
      if v == vertex:
        in_next = in_count + 1
      else:
        in_next = in_count
      if u == vertex:
        out_next = out_count + 1
      else:
        out_next = out_count
      return degree_at(edges.tail, vertex, in_next, out_next)
