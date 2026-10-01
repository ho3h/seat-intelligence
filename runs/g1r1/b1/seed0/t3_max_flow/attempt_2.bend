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
        edges = build_edges(input_edges, n)
        m = list_len(edges)
        return max_flow(edges, m, n, s, t, (0, 0))

def build_edges(xs, n):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, w) = xs.head
      tail = build_edges(xs.tail, n)
      if u < n:
        if v < n:
          return List/Cons((u, v, (w, 0), (0, 0)), tail)
        else:
          return tail
      else:
        return tail

def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)

def get_parent(xs, i):
  match xs:
    case List/Nil:
      return (0, 0, 0)
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_parent(xs.tail, i - 1)

def get_edge(xs, i):
  match xs:
    case List/Nil:
      return (0, 0, (0, 0), (0, 0))
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_edge(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def make_parents(k, sentinel):
  if k == 0:
    return []
  else:
    return List/Cons((0, sentinel, 0), make_parents(k - 1, sentinel))

def pair_add(a, b):
  (alo, ahi) = a
  (blo, bhi) = b
  lo = alo + blo
  if lo < alo:
    return (lo, ahi + bhi + 1)
  else:
    return (lo, ahi + bhi)

def pair_sub(a, b):
  (alo, ahi) = a
  (blo, bhi) = b
  lo = alo - blo
  if alo < blo:
    return (lo, ahi - bhi - 1)
  else:
    return (lo, ahi - bhi)

def pair_less(a, b):
  (alo, ahi) = a
  (blo, bhi) = b
  if ahi < bhi:
    return 1
  else:
    if ahi > bhi:
      return 0
    else:
      if alo < blo:
        return 1
      else:
        return 0

def pair_positive(a):
  (lo, hi) = a
  if hi != 0:
    return 1
  else:
    if lo != 0:
      return 1
    else:
      return 0

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))

def try_candidate(v, prev, edge_id, direction, cap, front, back, parents, n, t, m):
  if pair_positive(cap) == 0:
    return (front, back, parents, 0)
  else:
    (_, seen_edge, _) = get_parent(parents, v)
    if seen_edge != m:
      return (front, back, parents, 0)
    else:
      parents2 = set_at(parents, v, (prev, edge_id, direction))
      if v == t:
        return (front, back, parents2, 1)
      else:
        back2 = List/Cons(v, back)
        return (front, back2, parents2, 0)

def scan_edges(u, es, edge_id, front, back, parents, n, t, m):
  match es:
    case List/Nil:
      return (front, back, parents, 0)
    case List/Cons:
      (a, b, forward_cap, reverse_cap) = es.head
      if u == a:
        result = try_candidate(
          b, u, edge_id, 0, forward_cap, front, back, parents, n, t, m
        )
        (front2, back2, parents2, found) = result
        if found == 1:
          return result
        else:
          return scan_edges(
            u, es.tail, edge_id + 1, front2, back2, parents2, n, t, m
          )
      else:
        if u == b:
          result = try_candidate(
            a, u, edge_id, 1, reverse_cap, front, back, parents, n, t, m
          )
          (front2, back2, parents2, found) = result
          if found == 1:
            return result
          else:
            return scan_edges(
              u, es.tail, edge_id + 1, front2, back2, parents2, n, t, m
            )
        else:
          return scan_edges(
            u, es.tail, edge_id + 1, front, back, parents, n, t, m
          )

def bfs(front, back, parents, edges, n, t, m):
  match front:
    case List/Nil:
      match back:
        case List/Nil:
          return parents
        case List/Cons:
          next_front = reverse_list(back, [])
          return bfs(next_front, [], parents, edges, n, t, m)
    case List/Cons:
      (front2, back2, parents2, found) = scan_edges(
        front.head, edges, 0, front.tail, back, parents, n, t, m
      )
      if found == 1:
        return parents2
      else:
        return bfs(front2, back2, parents2, edges, n, t, m)

def path_min(node, source, parents, edges, best):
  if node == source:
    return best
  else:
    (prev, edge_id, direction) = get_parent(parents, node)
    (_, _, forward_cap, reverse_cap) = get_edge(edges, edge_id)
    if direction == 0:
      cap = forward_cap
    else:
      cap = reverse_cap
    if pair_less(cap, best) == 1:
      return path_min(prev, source, parents, edges, cap)
    else:
      return path_min(prev, source, parents, edges, best)

def augment_path(node, source, parents, edges, amount):
  if node == source:
    return edges
  else:
    (prev, edge_id, direction) = get_parent(parents, node)
    (u, v, forward_cap, reverse_cap) = get_edge(edges, edge_id)
    if direction == 0:
      forward2 = pair_sub(forward_cap, amount)
      reverse2 = pair_add(reverse_cap, amount)
    else:
      forward2 = pair_add(forward_cap, amount)
      reverse2 = pair_sub(reverse_cap, amount)
    edges2 = set_at(edges, edge_id, (u, v, forward2, reverse2))
    return augment_path(prev, source, parents, edges2, amount)

def max_flow(edges, m, n, source, sink, flow):
  parents0 = make_parents(n, m)
  parents1 = set_at(parents0, source, (source, m, 0))
  parents2 = bfs(
    List/Cons(source, []), [], parents1, edges, n, sink, m
  )
  (_, sink_edge, _) = get_parent(parents2, sink)
  if sink_edge == m:
    (flow_low, flow_high) = flow
    return flow_low
  else:
    amount = path_min(
      sink, source, parents2, edges, (16777215, 16777215)
    )
    edges2 = augment_path(sink, source, parents2, edges, amount)
    flow2 = pair_add(flow, amount)
    return max_flow(edges2, m, n, source, sink, flow2)
