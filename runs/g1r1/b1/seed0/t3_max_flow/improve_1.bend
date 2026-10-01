def prog(x):
  (n, s, t, input_edges) = x
  if s == t:
    return 0
  else:
    if s >= n:
      return 0
    else:
      if t >= n:
        return 0
      else:
        (adj, m) = build_graph(input_edges, n, make_adj(n), 0)
        return max_flow(adj, n, m, s, t, 0)

def make_adj(k):
  if k == 0:
    return []
  else:
    return List/Cons([], make_adj(k - 1))

def get_adj(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_adj(xs.tail, i - 1)

def get_parent(xs, i):
  match xs:
    case List/Nil:
      return (0, 0, 0, 0)
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_parent(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def add_arc(adj, vertex, arc):
  arcs = get_adj(adj, vertex)
  return set_at(adj, vertex, List/Cons(arc, arcs))

def build_graph(xs, n, adj, eid):
  match xs:
    case List/Nil:
      return (adj, eid)
    case List/Cons:
      (u, v, w) = xs.head
      if u < n:
        if v < n:
          adj1 = add_arc(adj, u, (v, eid, 0, w))
          adj2 = add_arc(adj1, v, (u, eid, 1, 0))
          return build_graph(xs.tail, n, adj2, eid + 1)
        else:
          return build_graph(xs.tail, n, adj, eid)
      else:
        return build_graph(xs.tail, n, adj, eid)

def make_parents(k, sentinel):
  if k == 0:
    return []
  else:
    return List/Cons((0, sentinel, 0, 0), make_parents(k - 1, sentinel))

def try_arc(v, prev, eid, direction, cap, back, parents, n, t, m):
  if cap == 0:
    return (back, parents, 0)
  else:
    (_, seen_eid, _, _) = get_parent(parents, v)
    if seen_eid != m:
      return (back, parents, 0)
    else:
      parents2 = set_at(parents, v, (prev, eid, direction, cap))
      if v == t:
        return (back, parents2, 1)
      else:
        return (List/Cons(v, back), parents2, 0)

def scan_arcs(u, arcs, back, parents, n, t, m):
  match arcs:
    case List/Nil:
      return (back, parents, 0)
    case List/Cons:
      (v, eid, direction, cap) = arcs.head
      result = try_arc(v, u, eid, direction, cap, back, parents, n, t, m)
      (back2, parents2, found) = result
      if found == 1:
        return result
      else:
        return scan_arcs(u, arcs.tail, back2, parents2, n, t, m)

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))

def bfs(front, back, parents, adj, n, t, m):
  match front:
    case List/Nil:
      match back:
        case List/Nil:
          return parents
        case List/Cons:
          next_front = reverse_list(back, [])
          return bfs(next_front, [], parents, adj, n, t, m)
    case List/Cons:
      arcs = get_adj(adj, front.head)
      (back2, parents2, found) = scan_arcs(
        front.head, arcs, back, parents, n, t, m
      )
      if found == 1:
        return parents2
      else:
        return bfs(front.tail, back2, parents2, adj, n, t, m)

def path_min(node, source, parents, best):
  if node == source:
    return best
  else:
    (prev, _, _, cap) = get_parent(parents, node)
    if cap < best:
      return path_min(prev, source, parents, cap)
    else:
      return path_min(prev, source, parents, best)

def update_arc_cap(arcs, eid, direction, amount, subtract):
  match arcs:
    case List/Nil:
      return []
    case List/Cons:
      (v, arc_eid, arc_direction, cap) = arcs.head
      if arc_eid == eid:
        if arc_direction == direction:
          if subtract == 1:
            return List/Cons(
              (v, arc_eid, arc_direction, cap - amount), arcs.tail
            )
          else:
            return List/Cons(
              (v, arc_eid, arc_direction, cap + amount), arcs.tail
            )
        else:
          return List/Cons(
            arcs.head,
            update_arc_cap(arcs.tail, eid, direction, amount, subtract)
          )
      else:
        return List/Cons(
          arcs.head,
          update_arc_cap(arcs.tail, eid, direction, amount, subtract)
        )

def augment_path(node, source, parents, adj, amount):
  if node == source:
    return adj
  else:
    (prev, eid, direction, _) = get_parent(parents, node)
    prev_arcs = get_adj(adj, prev)
    prev_arcs2 = update_arc_cap(prev_arcs, eid, direction, amount, 1)
    adj2 = set_at(adj, prev, prev_arcs2)
    node_arcs = get_adj(adj2, node)
    if direction == 0:
      node_arcs2 = update_arc_cap(node_arcs, eid, 1, amount, 0)
      adj3 = set_at(adj2, node, node_arcs2)
      return augment_path(prev, source, parents, adj3, amount)
    else:
      node_arcs2 = update_arc_cap(node_arcs, eid, 0, amount, 0)
      adj3 = set_at(adj2, node, node_arcs2)
      return augment_path(prev, source, parents, adj3, amount)

def max_flow(adj, n, m, source, sink, flow):
  parents0 = make_parents(n, m)
  parents1 = set_at(parents0, source, (source, m + 1, 0, 0))
  parents2 = bfs(
    List/Cons(source, []), [], parents1, adj, n, sink, m
  )
  (_, sink_eid, _, _) = get_parent(parents2, sink)
  if sink_eid == m:
    return flow
  else:
    amount = path_min(sink, source, parents2, 16777215)
    adj2 = augment_path(sink, source, parents2, adj, amount)
    return max_flow(adj2, n, m, source, sink, flow + amount)
