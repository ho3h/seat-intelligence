def prog(x):
  (n, s, t, edges) = x
  if s >= n:
    return 0
  else:
    if t >= n:
      return 0
    else:
      if s == t:
        return 1
      else:
        adj0 = make_vals(n, [])
        adj = build_adj(edges, n, adj0)
        dist0 = make_vals(n, 16777215)
        ways0 = make_vals(n, 0)
        dist = set_at(dist0, s, 0)
        ways = set_at(ways0, s, 1)
        return bfs(adj, n, dist, ways, [s], 0, t)

def make_vals(n, value):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(value, make_vals(n - 1, value))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
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

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def add_neighbor(adj, v, w):
  neighbors = get_at(adj, v)
  if contains(neighbors, w) == 1:
    return adj
  else:
    return set_at(adj, v, List/Cons(w, neighbors))

def build_adj(edges, n, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (a, b) = edges.head
      if a < n:
        if b < n:
          adj1 = add_neighbor(adj, a, b)
          adj2 = add_neighbor(adj1, b, a)
          return build_adj(edges.tail, n, adj2)
        else:
          return build_adj(edges.tail, n, adj)
      else:
        return build_adj(edges.tail, n, adj)

def bfs(adj, n, dist, ways, frontier, depth, target):
  match frontier:
    case List/Nil:
      return get_at(ways, target)
    case List/Cons:
      (dist2, ways2, next_frontier) = expand_frontier(
        frontier, adj, dist, ways, depth, []
      )
      if get_at(dist2, target) != 16777215:
        return get_at(ways2, target)
      else:
        return bfs(adj, n, dist2, ways2, next_frontier, depth + 1, target)

def expand_frontier(frontier, adj, dist, ways, depth, next_frontier):
  match frontier:
    case List/Nil:
      return (dist, ways, next_frontier)
    case List/Cons:
      neighbors = get_at(adj, frontier.head)
      (dist2, ways2, next2) = expand_neighbors(
        frontier.head, neighbors, dist, ways, depth, next_frontier
      )
      return expand_frontier(
        frontier.tail, adj, dist2, ways2, depth, next2
      )

def expand_neighbors(v, neighbors, dist, ways, depth, next_frontier):
  match neighbors:
    case List/Nil:
      return (dist, ways, next_frontier)
    case List/Cons:
      w = neighbors.head
      old_dist = get_at(dist, w)
      if old_dist == 16777215:
        dist2 = set_at(dist, w, depth + 1)
        ways2 = set_at(ways, w, get_at(ways, v))
        next2 = List/Cons(w, next_frontier)
        return expand_neighbors(
          v, neighbors.tail, dist2, ways2, depth, next2
        )
      else:
        if old_dist == depth + 1:
          ways2 = set_at(ways, w, get_at(ways, w) + get_at(ways, v))
          return expand_neighbors(
            v, neighbors.tail, dist, ways2, depth, next_frontier
          )
        else:
          return expand_neighbors(
            v, neighbors.tail, dist, ways, depth, next_frontier
          )
