def prog(x):
  (n, edges) = x
  adj = make_empty_adj(n)
  adj2 = build_adj(edges, adj)
  disc = make_zeros(n)
  low = make_zeros(n)
  art = make_zeros(n)
  state = run_roots(0, n, adj2, disc, low, art, 1)
  (dl, at) = state
  (disc2, low2) = dl
  (art2, timer) = at
  return collect_cuts(0, n, art2)

def make_zeros(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, make_zeros(n - 1))

def make_empty_adj(n):
  if n == 0:
    return []
  else:
    return List/Cons([], make_empty_adj(n - 1))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def replace_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, replace_at(xs.tail, i - 1, value))

def append_value(xs, value):
  match xs:
    case List/Nil:
      return List/Cons(value, [])
    case List/Cons:
      return List/Cons(xs.head, append_value(xs.tail, value))

def push_neighbor(adj, u, v):
  neighbors = get_at(adj, u)
  updated = append_value(neighbors, v)
  return replace_at(adj, u, updated)

def build_adj(edges, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = push_neighbor(adj, u, v)
      adj2 = push_neighbor(adj1, v, u)
      return build_adj(edges.tail, adj2)

def run_roots(i, n, adj, disc, low, art, timer):
  if i == n:
    return ((disc, low), (art, timer))
  else:
    if get_at(disc, i) == 0:
      state = visit(i, n, n, adj, disc, low, art, timer)
      (dl, at) = state
      (disc2, low2) = dl
      (art2, timer2) = at
      return run_roots(i + 1, n, adj, disc2, low2, art2, timer2)
    else:
      return run_roots(i + 1, n, adj, disc, low, art, timer)

def visit(u, parent, n, adj, disc, low, art, timer):
  disc2 = replace_at(disc, u, timer)
  low2 = replace_at(low, u, timer)
  neighbors = get_at(adj, u)
  return visit_neighbors(u, parent, n, adj, neighbors, disc2, low2, art, timer + 1, 0)

def visit_neighbors(u, parent, n, adj, neighbors, disc, low, art, timer, children):
  match neighbors:
    case List/Nil:
      if parent == n:
        if children > 1:
          art2 = replace_at(art, u, 1)
          return ((disc, low), (art2, timer))
        else:
          return ((disc, low), (art, timer))
      else:
        return ((disc, low), (art, timer))
    case List/Cons:
      v = neighbors.head
      if v == parent:
        return visit_neighbors(u, parent, n, adj, neighbors.tail, disc, low, art, timer, children)
      else:
        dv = get_at(disc, v)
        if dv == 0:
          state = visit(v, u, n, adj, disc, low, art, timer)
          (dl, at) = state
          (disc2, low2) = dl
          (art2, timer2) = at
          lowv = get_at(low2, v)
          lowu = get_at(low2, u)
          if lowv < lowu:
            low3 = replace_at(low2, u, lowv)
          else:
            low3 = low2
          if parent != n:
            if lowv >= get_at(disc2, u):
              art3 = replace_at(art2, u, 1)
            else:
              art3 = art2
          else:
            art3 = art2
          return visit_neighbors(u, parent, n, adj, neighbors.tail, disc2, low3, art3, timer2, children + 1)
        else:
          lowu = get_at(low, u)
          if dv < lowu:
            low2 = replace_at(low, u, dv)
          else:
            low2 = low
          return visit_neighbors(u, parent, n, adj, neighbors.tail, disc, low2, art, timer, children)

def collect_cuts(i, n, art):
  if i == n:
    return []
  else:
    rest = collect_cuts(i + 1, n, art)
    if get_at(art, i) == 1:
      return List/Cons(i, rest)
    else:
      return rest
