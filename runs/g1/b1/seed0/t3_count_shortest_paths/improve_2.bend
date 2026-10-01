type Vec: VLeaf { value } | VNode { left, right }

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
        cap = vec_capacity(n, 1)
        adj0 = make_vec(cap, [])
        adj = build_adj(edges, n, cap, adj0)
        dist0 = make_vec(cap, 16777215)
        ways0 = make_vec(cap, 0)
        dist = vec_set(dist0, s, cap, 0)
        ways = vec_set(ways0, s, cap, 1)
        return bfs(adj, cap, dist, ways, [s], 0, t)

def vec_capacity(n, cap):
  if cap >= n:
    return cap
  else:
    return vec_capacity(n, cap * 2)

def make_vec(size, value):
  if size == 1:
    return Vec/VLeaf(value)
  else:
    half = size / 2
    left = make_vec(half, value)
    right = make_vec(half, value)
    return Vec/VNode(left, right)

def vec_get(vec, index, size):
  match vec:
    case Vec/VLeaf:
      return vec.value
    case Vec/VNode:
      half = size / 2
      if index < half:
        return vec_get(vec.left, index, half)
      else:
        return vec_get(vec.right, index - half, half)

def vec_set(vec, index, size, value):
  match vec:
    case Vec/VLeaf:
      return Vec/VLeaf(value)
    case Vec/VNode:
      half = size / 2
      if index < half:
        return Vec/VNode(vec_set(vec.left, index, half, value), vec.right)
      else:
        return Vec/VNode(vec.left, vec_set(vec.right, index - half, half, value))

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def add_neighbor(adj, v, w, cap):
  neighbors = vec_get(adj, v, cap)
  if contains(neighbors, w) == 1:
    return adj
  else:
    return vec_set(adj, v, cap, List/Cons(w, neighbors))

def build_adj(edges, n, cap, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (a, b) = edges.head
      if a < n:
        if b < n:
          adj1 = add_neighbor(adj, a, b, cap)
          adj2 = add_neighbor(adj1, b, a, cap)
          return build_adj(edges.tail, n, cap, adj2)
        else:
          return build_adj(edges.tail, n, cap, adj)
      else:
        return build_adj(edges.tail, n, cap, adj)

def bfs(adj, cap, dist, ways, frontier, depth, target):
  match frontier:
    case List/Nil:
      return vec_get(ways, target, cap)
    case List/Cons:
      (dist2, ways2, next_frontier) = expand_frontier(
        frontier, adj, cap, dist, ways, depth, []
      )
      if vec_get(dist2, target, cap) != 16777215:
        return vec_get(ways2, target, cap)
      else:
        return bfs(adj, cap, dist2, ways2, next_frontier, depth + 1, target)

def expand_frontier(frontier, adj, cap, dist, ways, depth, next_frontier):
  match frontier:
    case List/Nil:
      return (dist, ways, next_frontier)
    case List/Cons:
      neighbors = vec_get(adj, frontier.head, cap)
      (dist2, ways2, next2) = expand_neighbors(
        frontier.head, neighbors, cap, dist, ways, depth, next_frontier
      )
      return expand_frontier(
        frontier.tail, adj, cap, dist2, ways2, depth, next2
      )

def expand_neighbors(v, neighbors, cap, dist, ways, depth, next_frontier):
  match neighbors:
    case List/Nil:
      return (dist, ways, next_frontier)
    case List/Cons:
      w = neighbors.head
      old_dist = vec_get(dist, w, cap)
      if old_dist == 16777215:
        dist2 = vec_set(dist, w, cap, depth + 1)
        ways2 = vec_set(ways, w, cap, vec_get(ways, v, cap))
        next2 = List/Cons(w, next_frontier)
        return expand_neighbors(
          v, neighbors.tail, cap, dist2, ways2, depth, next2
        )
      else:
        if old_dist == depth + 1:
          ways2 = vec_set(
            ways, w, cap, vec_get(ways, w, cap) + vec_get(ways, v, cap)
          )
          return expand_neighbors(
            v, neighbors.tail, cap, dist, ways2, depth, next_frontier
          )
        else:
          return expand_neighbors(
            v, neighbors.tail, cap, dist, ways, depth, next_frontier
          )
