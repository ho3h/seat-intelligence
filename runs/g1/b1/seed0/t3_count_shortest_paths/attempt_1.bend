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
        dist0 = make_vals(n, 16777215)
        ways0 = make_vals(n, 0)
        dist1 = set_at(dist0, s, 0)
        ways1 = set_at(ways0, s, 1)
        ways2 = bfs(edges, n, dist1, ways1, [s], 0)
        return get_at(ways2, t)

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

def bfs(edges, n, dist, ways, frontier, depth):
  match frontier:
    case List/Nil:
      return ways
    case List/Cons:
      (dist2, ways2, next_frontier) = spread_frontier(
        frontier, edges, n, depth, dist, ways, []
      )
      return bfs(edges, n, dist2, ways2, next_frontier, depth + 1)

def spread_frontier(frontier, edges, n, depth, dist, ways, next_frontier):
  match frontier:
    case List/Nil:
      return (dist, ways, next_frontier)
    case List/Cons:
      (dist2, ways2, next2) = spread_edges(
        frontier.head, edges, [], n, depth, dist, ways, next_frontier
      )
      return spread_frontier(
        frontier.tail, edges, n, depth, dist2, ways2, next2
      )

def spread_edges(v, edges, seen, n, depth, dist, ways, next_frontier):
  match edges:
    case List/Nil:
      return (dist, ways, next_frontier)
    case List/Cons:
      (a, b) = edges.head
      if a == v:
        return consider_neighbor(
          v, b, edges.tail, seen, n, depth, dist, ways, next_frontier
        )
      else:
        if b == v:
          return consider_neighbor(
            v, a, edges.tail, seen, n, depth, dist, ways, next_frontier
          )
        else:
          return spread_edges(
            v, edges.tail, seen, n, depth, dist, ways, next_frontier
          )

def consider_neighbor(v, w, rest, seen, n, depth, dist, ways, next_frontier):
  if w >= n:
    return spread_edges(v, rest, seen, n, depth, dist, ways, next_frontier)
  else:
    if contains(seen, w) == 1:
      return spread_edges(v, rest, seen, n, depth, dist, ways, next_frontier)
    else:
      seen2 = List/Cons(w, seen)
      old_dist = get_at(dist, w)
      if old_dist == 16777215:
        dist2 = set_at(dist, w, depth + 1)
        ways_v = get_at(ways, v)
        ways2 = set_at(ways, w, ways_v)
        next2 = List/Cons(w, next_frontier)
        return spread_edges(v, rest, seen2, n, depth, dist2, ways2, next2)
      else:
        if old_dist == depth + 1:
          ways_v = get_at(ways, v)
          ways_w = get_at(ways, w)
          ways2 = set_at(ways, w, ways_w + ways_v)
          return spread_edges(v, rest, seen2, n, depth, dist, ways2, next_frontier)
        else:
          return spread_edges(v, rest, seen2, n, depth, dist, ways, next_frontier)
