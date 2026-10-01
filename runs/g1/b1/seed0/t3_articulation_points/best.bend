def prog(x):
  (n, edges) = x
  size = capacity(n, 1)
  adj = make_empty_adj(size)
  adj2 = build_adj(edges, adj, size)
  disc = make_zeros(size)
  low = make_zeros(size)
  art = make_zeros(size)
  state = run_roots(0, n, size, adj2, disc, low, art, 1)
  (dl, at) = state
  (disc2, low2) = dl
  (art2, timer) = at
  return collect_cuts(0, n, size, art2)

def capacity(n, size):
  if size >= n:
    return size
  else:
    return capacity(n, size * 2)

def make_zeros(size):
  if size == 1:
    return 0
  else:
    half = size / 2
    return (make_zeros(half), make_zeros(half))

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
  updated = List/Cons(v, neighbors)
  return array_set(adj, u, updated, size)

def build_adj(edges, adj, size):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = push_neighbor(adj, u, v, size)
      adj2 = push_neighbor(adj1, v, u, size)
      return build_adj(edges.tail, adj2, size)

def run_roots(i, n, size, adj, disc, low, art, timer):
  if i == n:
    return ((disc, low), (art, timer))
  else:
    if array_get(disc, i, size) == 0:
      state = visit(i, n, n, size, adj, disc, low, art, timer)
      (dl, at) = state
      (disc2, low2) = dl
      (art2, timer2) = at
      return run_roots(i + 1, n, size, adj, disc2, low2, art2, timer2)
    else:
      return run_roots(i + 1, n, size, adj, disc, low, art, timer)

def visit(u, parent, n, size, adj, disc, low, art, timer):
  disc2 = array_set(disc, u, timer, size)
  low2 = array_set(low, u, timer, size)
  neighbors = array_get(adj, u, size)
  return visit_neighbors(u, parent, n, size, adj, neighbors, disc2, low2, art, timer + 1, 0)

def visit_neighbors(u, parent, n, size, adj, neighbors, disc, low, art, timer, children):
  match neighbors:
    case List/Nil:
      if parent == n:
        if children > 1:
          art2 = array_set(art, u, 1, size)
          return ((disc, low), (art2, timer))
        else:
          return ((disc, low), (art, timer))
      else:
        return ((disc, low), (art, timer))
    case List/Cons:
      v = neighbors.head
      if v == parent:
        return visit_neighbors(u, parent, n, size, adj, neighbors.tail, disc, low, art, timer, children)
      else:
        dv = array_get(disc, v, size)
        if dv == 0:
          state = visit(v, u, n, size, adj, disc, low, art, timer)
          (dl, at) = state
          (disc2, low2) = dl
          (art2, timer2) = at
          lowv = array_get(low2, v, size)
          lowu = array_get(low2, u, size)
          if lowv < lowu:
            low3 = array_set(low2, u, lowv, size)
          else:
            low3 = low2
          if parent != n:
            if lowv >= array_get(disc2, u, size):
              art3 = array_set(art2, u, 1, size)
            else:
              art3 = art2
          else:
            art3 = art2
          return visit_neighbors(u, parent, n, size, adj, neighbors.tail, disc2, low3, art3, timer2, children + 1)
        else:
          lowu = array_get(low, u, size)
          if dv < lowu:
            low2 = array_set(low, u, dv, size)
          else:
            low2 = low
          return visit_neighbors(u, parent, n, size, adj, neighbors.tail, disc, low2, art, timer, children)

def collect_cuts(i, n, size, art):
  if i == n:
    return []
  else:
    rest = collect_cuts(i + 1, n, size, art)
    if array_get(art, i, size) == 1:
      return List/Cons(i, rest)
    else:
      return rest
