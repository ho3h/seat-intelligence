def prog(x):
  (n, s, t, edges) = x
  if s == t:
    return 0
  else:
    if s >= n:
      return 0
    else:
      if t >= n:
        return 0
      else:
        caps = make_zeros(n * n)
        caps2 = load_edges(edges, n, caps)
        return max_flow(caps2, n, s, t, (0, 0))

def make_zeros(k):
  if k == 0:
    return []
  else:
    return List/Cons((0, 0), make_zeros(k - 1))

def make_values(k, value):
  if k == 0:
    return []
  else:
    return List/Cons(value, make_values(k - 1, value))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def load_edges(edges, n, caps):
  match edges:
    case List/Nil:
      return caps
    case List/Cons:
      (u, v, w) = edges.head
      if u < n:
        if v < n:
          index = u * n + v
          old = get_at(caps, index)
          updated = pair_add(old, (w, 0))
          caps2 = set_at(caps, index, updated)
          return load_edges(edges.tail, n, caps2)
        else:
          return load_edges(edges.tail, n, caps)
      else:
        return load_edges(edges.tail, n, caps)

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

def bfs(front, back, parents, residual, n, t):
  match front:
    case List/Nil:
      match back:
        case List/Nil:
          return parents
        case List/Cons:
          next_front = reverse_list(back, [])
          return bfs(next_front, [], parents, residual, n, t)
    case List/Cons:
      (front2, back2, parents2, found) = scan_neighbors(
        front.head, 0, n, front.tail, back, parents, residual, n, t
      )
      if found == 1:
        return parents2
      else:
        return bfs(front2, back2, parents2, residual, n, t)

def scan_neighbors(u, v, n, front, back, parents, residual, graph_n, t):
  if v == n:
    return (front, back, parents, 0)
  else:
    parent = get_at(parents, v)
    if parent == graph_n:
      cap = get_at(residual, u * graph_n + v)
      if pair_positive(cap) == 1:
        parents2 = set_at(parents, v, u)
        if v == t:
          return (front, back, parents2, 1)
        else:
          back2 = List/Cons(v, back)
          return scan_neighbors(
            u, v + 1, n, front, back2, parents2, residual, graph_n, t
          )
      else:
        return scan_neighbors(
          u, v + 1, n, front, back, parents, residual, graph_n, t
        )
    else:
      return scan_neighbors(
        u, v + 1, n, front, back, parents, residual, graph_n, t
      )

def path_min(node, source, parents, residual, n, best):
  if node == source:
    return best
  else:
    parent = get_at(parents, node)
    cap = get_at(residual, parent * n + node)
    if pair_less(cap, best) == 1:
      return path_min(parent, source, parents, residual, n, cap)
    else:
      return path_min(parent, source, parents, residual, n, best)

def augment_path(node, source, parents, residual, n, amount):
  if node == source:
    return residual
  else:
    parent = get_at(parents, node)
    forward_index = parent * n + node
    forward = pair_sub(get_at(residual, forward_index), amount)
    residual2 = set_at(residual, forward_index, forward)
    reverse_index = node * n + parent
    reverse = pair_add(get_at(residual2, reverse_index), amount)
    residual3 = set_at(residual2, reverse_index, reverse)
    return augment_path(parent, source, parents, residual3, n, amount)

def max_flow(residual, n, source, sink, flow):
  parents0 = make_values(n, n)
  parents1 = set_at(parents0, source, source)
  parents2 = bfs(
    List/Cons(source, []), [], parents1, residual, n, sink
  )
  if get_at(parents2, sink) == n:
    (flow_low, flow_high) = flow
    return flow_low
  else:
    amount = path_min(
      sink, source, parents2, residual, n, (16777215, 16777215)
    )
    residual2 = augment_path(
      sink, source, parents2, residual, n, amount
    )
    flow2 = pair_add(flow, amount)
    return max_flow(residual2, n, source, sink, flow2)
