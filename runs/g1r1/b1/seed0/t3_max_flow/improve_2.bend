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
        span = tree_span(n, 1)
        empty_adj = make_tree(span)
        (adj, m) = build_graph(input_edges, n, span, empty_adj, 0)
        return max_flow(adj, span, n, m, s, t, 0)

def tree_span(n, span):
  if span >= n:
    return span
  else:
    return tree_span(n, span * 2)

def make_tree(span):
  if span == 1:
    return []
  else:
    half = span / 2
    return (make_tree(half), make_tree(half))

def make_parents(span, sentinel):
  if span == 1:
    return (0, sentinel, 0, 0)
  else:
    half = span / 2
    return (make_parents(half, sentinel), make_parents(half, sentinel))

def tree_get(tree, index, span):
  if span == 1:
    return tree
  else:
    (left, right) = tree
    half = span / 2
    if index < half:
      return tree_get(left, index, half)
    else:
      return tree_get(right, index - half, half)

def tree_set(tree, index, value, span):
  if span == 1:
    return value
  else:
    (left, right) = tree
    half = span / 2
    if index < half:
      return (tree_set(left, index, value, half), right)
    else:
      return (left, tree_set(right, index - half, value, half))

def add_arc(adj, vertex, arc, span):
  arcs = tree_get(adj, vertex, span)
  adj2 = tree_set(adj, vertex, List/Cons(arc, arcs), span)
  return adj2

def build_graph(xs, n, span, adj, eid):
  match xs:
    case List/Nil:
      return (adj, eid)
    case List/Cons:
      (u, v, w) = xs.head
      if u < n:
        if v < n:
          adj1 = add_arc(adj, u, (v, eid, 0, w), span)
          adj2 = add_arc(adj1, v, (u, eid, 1, 0), span)
          return build_graph(xs.tail, n, span, adj2, eid + 1)
        else:
          return build_graph(xs.tail, n, span, adj, eid)
      else:
        return build_graph(xs.tail, n, span, adj, eid)

def get_arc(xs, i):
  match xs:
    case List/Nil:
      return (0, 0, 0, 0)
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_arc(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def try_arc(v, prev, eid, direction, cap, back, parents, span, t, m):
  if cap == 0:
    return (back, parents, 0)
  else:
    (_, seen_eid, _, _) = tree_get(parents, v, span)
    if seen_eid != m:
      return (back, parents, 0)
    else:
      parents2 = tree_set(parents, v, (prev, eid, direction, cap), span)
      if v == t:
        return (back, parents2, 1)
      else:
        return (List/Cons(v, back), parents2, 0)

def scan_arcs(u, arcs, back, parents, span, t, m):
  match arcs:
    case List/Nil:
      return (back, parents, 0)
    case List/Cons:
      (v, eid, direction, cap) = arcs.head
      result = try_arc(
        v, u, eid, direction, cap, back, parents, span, t, m
      )
      (back2, parents2, found) = result
      if found == 1:
        return result
      else:
        return scan_arcs(u, arcs.tail, back2, parents2, span, t, m)

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))

def bfs(front, back, parents, adj, span, t, m):
  match front:
    case List/Nil:
      match back:
        case List/Nil:
          return parents
        case List/Cons:
          next_front = reverse_list(back, [])
          return bfs(next_front, [], parents, adj, span, t, m)
    case List/Cons:
      arcs = tree_get(adj, front.head, span)
      (back2, parents2, found) = scan_arcs(
        front.head, arcs, back, parents, span, t, m
      )
      if found == 1:
        return parents2
      else:
        return bfs(front.tail, back2, parents2, adj, span, t, m)

def path_min(node, source, parents, span, best):
  if node == source:
    return best
  else:
    (prev, _, _, cap) = tree_get(parents, node, span)
    if cap < best:
      return path_min(prev, source, parents, span, cap)
    else:
      return path_min(prev, source, parents, span, best)

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

def augment_path(node, source, parents, adj, span, amount):
  if node == source:
    return adj
  else:
    (prev, eid, direction, _) = tree_get(parents, node, span)
    prev_arcs = tree_get(adj, prev, span)
    prev_arcs2 = update_arc_cap(prev_arcs, eid, direction, amount, 1)
    adj2 = tree_set(adj, prev, prev_arcs2, span)
    node_arcs = tree_get(adj2, node, span)
    if direction == 0:
      node_arcs2 = update_arc_cap(node_arcs, eid, 1, amount, 0)
      adj3 = tree_set(adj2, node, node_arcs2, span)
      return augment_path(prev, source, parents, adj3, span, amount)
    else:
      node_arcs2 = update_arc_cap(node_arcs, eid, 0, amount, 0)
      adj3 = tree_set(adj2, node, node_arcs2, span)
      return augment_path(prev, source, parents, adj3, span, amount)

def max_flow(adj, span, n, m, source, sink, flow):
  parents0 = make_parents(span, m)
  parents1 = tree_set(parents0, source, (source, m + 1, 0, 0), span)
  parents2 = bfs(
    List/Cons(source, []), [], parents1, adj, span, sink, m
  )
  (_, sink_eid, _, _) = tree_get(parents2, sink, span)
  if sink_eid == m:
    return flow
  else:
    amount = path_min(sink, source, parents2, span, 16777215)
    adj2 = augment_path(sink, source, parents2, adj, span, amount)
    return max_flow(adj2, span, n, m, source, sink, flow + amount)
