def prog(x):
  (n, s, k, edges) = x
  cap = capacity(n, 1)
  adj = build_adj(edges, make_adj(cap), cap)
  seen = mark(make_seen(cap), s, cap)
  frontier = List/Cons(s, List/Nil)
  return bfs(adj, frontier, seen, cap, k, 1)

def capacity(n, cap):
  if cap >= n:
    return cap
  else:
    return capacity(n, cap * 2)

def make_adj(size):
  if size == 1:
    return List/Nil
  else:
    child = make_adj(size / 2)
    return (child, child)

def make_seen(size):
  if size == 1:
    return 0
  else:
    child = make_seen(size / 2)
    return (child, child)

def add_adj(tree, index, size, vertex):
  if size == 1:
    return List/Cons(vertex, tree)
  else:
    (left, right) = tree
    half = size / 2
    if index < half:
      new_left = add_adj(left, index, half, vertex)
      return (new_left, right)
    else:
      new_right = add_adj(right, index - half, half, vertex)
      return (left, new_right)

def get_adj(tree, index, size):
  if size == 1:
    return tree
  else:
    (left, right) = tree
    half = size / 2
    if index < half:
      return get_adj(left, index, half)
    else:
      return get_adj(right, index - half, half)

def is_marked(tree, index, size):
  if size == 1:
    return tree
  else:
    (left, right) = tree
    half = size / 2
    if index < half:
      return is_marked(left, index, half)
    else:
      return is_marked(right, index - half, half)

def mark(tree, index, size):
  if size == 1:
    return 1
  else:
    (left, right) = tree
    half = size / 2
    if index < half:
      new_left = mark(left, index, half)
      return (new_left, right)
    else:
      new_right = mark(right, index - half, half)
      return (left, new_right)

def build_adj(edges, adj, size):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = add_adj(adj, u, size, v)
      adj2 = add_adj(adj1, v, size, u)
      return build_adj(edges.tail, adj2, size)

def visit_neighbors(neighbors, seen, nxt, total, size):
  match neighbors:
    case List/Nil:
      return (seen, nxt, total)
    case List/Cons:
      vertex = neighbors.head
      if is_marked(seen, vertex, size) == 1:
        return visit_neighbors(neighbors.tail, seen, nxt, total, size)
      else:
        seen1 = mark(seen, vertex, size)
        nxt1 = List/Cons(vertex, nxt)
        return visit_neighbors(neighbors.tail, seen1, nxt1, total + 1, size)

def process_frontier(frontier, adj, seen, nxt, total, size):
  match frontier:
    case List/Nil:
      return (seen, nxt, total)
    case List/Cons:
      neighbors = get_adj(adj, frontier.head, size)
      (seen1, nxt1, total1) = visit_neighbors(neighbors, seen, nxt, total, size)
      return process_frontier(frontier.tail, adj, seen1, nxt1, total1, size)

def bfs(adj, frontier, seen, size, remaining, total):
  if remaining == 0:
    return total
  else:
    match frontier:
      case List/Nil:
        return total
      case List/Cons:
        (seen1, nxt, total1) = process_frontier(frontier, adj, seen, List/Nil, total, size)
        return bfs(adj, nxt, seen1, size, remaining - 1, total1)
