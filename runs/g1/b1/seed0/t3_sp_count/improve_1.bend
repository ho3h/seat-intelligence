def prog(x):
  (n, s, t, edges) = x
  if s == t:
    return 1
  else:
    dist0 = fill(n, n)
    ways0 = fill(n, 0)
    dist = set_at(dist0, s, 0)
    ways = set_at(ways0, s, 1)
    return bfs(n, t, edges, dist, ways, [s], 0)

def fill(k, value):
  switch k:
    case 0:
      return []
    case _:
      tail = fill(k - 1, value)
      return List/Cons(value, tail)

def get_at(xs, i):
  switch i:
    case 0:
      match xs:
        case List/Nil:
          return 0
        case List/Cons:
          return xs.head
    case _:
      match xs:
        case List/Nil:
          return 0
        case List/Cons:
          return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  switch i:
    case 0:
      match xs:
        case List/Nil:
          return []
        case List/Cons:
          return List/Cons(value, xs.tail)
    case _:
      match xs:
        case List/Nil:
          return []
        case List/Cons:
          tail = set_at(xs.tail, i - 1, value)
          return List/Cons(xs.head, tail)

def update_edge(n, level, v, source_ways, dist, ways, next_frontier):
  dv = get_at(dist, v)
  if dv == n:
    dist2 = set_at(dist, v, level + 1)
    ways2 = set_at(ways, v, source_ways)
    next2 = List/Cons(v, next_frontier)
    return (dist2, ways2, next2)
  else:
    if dv == level + 1:
      old_ways = get_at(ways, v)
      ways2 = set_at(ways, v, old_ways + source_ways)
      return (dist, ways2, next_frontier)
    else:
      return (dist, ways, next_frontier)

def scan_edges(edges, source, n, level, source_ways, dist, ways, next_frontier):
  match edges:
    case List/Nil:
      return (dist, ways, next_frontier)
    case List/Cons:
      (u, v) = edges.head
      if u == source:
        (dist2, ways2, next2) = update_edge(n, level, v, source_ways, dist, ways, next_frontier)
        return scan_edges(edges.tail, source, n, level, source_ways, dist2, ways2, next2)
      else:
        return scan_edges(edges.tail, source, n, level, source_ways, dist, ways, next_frontier)

def scan_frontier(frontier, edges, n, level, dist, ways, next_frontier):
  match frontier:
    case List/Nil:
      return (dist, ways, next_frontier)
    case List/Cons:
      source = frontier.head
      source_ways = get_at(ways, source)
      (dist2, ways2, next2) = scan_edges(edges, source, n, level, source_ways, dist, ways, next_frontier)
      return scan_frontier(frontier.tail, edges, n, level, dist2, ways2, next2)

def bfs(n, t, edges, dist, ways, frontier, level):
  match frontier:
    case List/Nil:
      return 0
    case List/Cons:
      (dist2, ways2, next_frontier) = scan_frontier(frontier, edges, n, level, dist, ways, [])
      if get_at(dist2, t) != n:
        return get_at(ways2, t)
      else:
        return bfs(n, t, edges, dist2, ways2, next_frontier, level + 1)
