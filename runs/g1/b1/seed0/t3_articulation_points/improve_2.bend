def prog(x):
  (n, edges) = x
  size = capacity(n, 1)
  adj = make_empty_adj(size)
  adj2 = build_adj(edges, adj, size)
  states = make_vertex_states(size)
  result = run_roots(0, n, size, adj2, states, 1)
  (states2, timer) = result
  return collect_cuts(0, n, size, states2)

def capacity(n, size):
  if size >= n:
    return size
  else:
    return capacity(n, size * 2)

def make_vertex_states(size):
  if size == 1:
    return (0, 0, 0)
  else:
    half = size / 2
    return (make_vertex_states(half), make_vertex_states(half))

def make_empty_adj(size):
  if size == 1:
    return []
  else:
    half = size / 2
    return (make_empty_adj(half), make_empty_adj(half))

def array_get(tree, i, size):
  if size == 1:
    return tree
  else:
    (left, right) = tree
    half = size / 2
    if i < half:
      return array_get(left, i, half)
    else:
      return array_get(right, i - half, half)

def array_set(tree, i, value, size):
  if size == 1:
    return value
  else:
    (left, right) = tree
    half = size / 2
    if i < half:
      left2 = array_set(left, i, value, half)
      return (left2, right)
    else:
      right2 = array_set(right, i - half, value, half)
      return (left, right2)

def push_neighbor(adj, u, v, size):
  neighbors = array_get(adj, u, size)
  return array_set(adj, u, List/Cons(v, neighbors), size)

def build_adj(edges, adj, size):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = push_neighbor(adj, u, v, size)
      adj2 = push_neighbor(adj1, v, u, size)
      return build_adj(edges.tail, adj2, size)

def run_roots(i, n, size, adj, states, timer):
  if i == n:
    return (states, timer)
  else:
    (disc, low, art) = array_get(states, i, size)
    if disc == 0:
      result = visit(i, n, n, size, adj, states, timer)
      (states2, timer2) = result
      return run_roots(i + 1, n, size, adj, states2, timer2)
    else:
      return run_roots(i + 1, n, size, adj, states, timer)

def visit(u, parent, n, size, adj, states, timer):
  states2 = array_set(states, u, (timer, timer, 0), size)
  neighbors = array_get(adj, u, size)
  return visit_neighbors(u, parent, n, size, adj, neighbors, states2, timer + 1, 0)

def visit_neighbors(u, parent, n, size, adj, neighbors, states, timer, children):
  match neighbors:
    case List/Nil:
      if parent == n:
        (disc, low, art) = array_get(states, u, size)
        if children > 1:
          states2 = array_set(states, u, (disc, low, 1), size)
          return (states2, timer)
        else:
          return (states, timer)
      else:
        return (states, timer)
    case List/Cons:
      v = neighbors.head
      if v == parent:
        return visit_neighbors(u, parent, n, size, adj, neighbors.tail, states, timer, children)
      else:
        (dv, lowv0, artv) = array_get(states, v, size)
        if dv == 0:
          result = visit(v, u, n, size, adj, states, timer)
          (states2, timer2) = result
          (disc_u, low_u, art_u) = array_get(states2, u, size)
          (disc_v, low_v, art_v) = array_get(states2, v, size)
          if low_v < low_u:
            low_new = low_v
          else:
            low_new = low_u
          if parent != n:
            if low_v >= disc_u:
              art_new = 1
            else:
              art_new = art_u
          else:
            art_new = art_u
          states3 = array_set(states2, u, (disc_u, low_new, art_new), size)
          return visit_neighbors(u, parent, n, size, adj, neighbors.tail, states3, timer2, children + 1)
        else:
          (disc_u, low_u, art_u) = array_get(states, u, size)
          if dv < low_u:
            states2 = array_set(states, u, (disc_u, dv, art_u), size)
          else:
            states2 = states
          return visit_neighbors(u, parent, n, size, adj, neighbors.tail, states2, timer, children)

def collect_cuts(i, n, size, states):
  if i == n:
    return []
  else:
    rest = collect_cuts(i + 1, n, size, states)
    (disc, low, art) = array_get(states, i, size)
    if art == 1:
      return List/Cons(i, rest)
    else:
      return rest
