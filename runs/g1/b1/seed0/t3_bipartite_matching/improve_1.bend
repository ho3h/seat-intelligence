def prog(x):
  (a, b, edges) = x
  adj = build_adj(0, a, edges)
  mtch = make_list(b, a)
  inf = a + 1
  return matching_phases(a, b, adj, mtch, 0, a, inf)

def make_list(n, value):
  if n == 0:
    return []
  else:
    return List/Cons(value, make_list(n - 1, value))

def build_adj(i, a, edges):
  if i == a:
    return []
  else:
    neighbors = collect_neighbors(i, edges, [])
    rest = build_adj(i + 1, a, edges)
    return List/Cons(neighbors, rest)

def collect_neighbors(target, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      if u == target:
        return collect_neighbors(target, edges.tail, List/Cons(v, acc))
      else:
        return collect_neighbors(target, edges.tail, acc)

def list_get(xs, i):
  if i == 0:
    match xs:
      case List/Nil:
        return 0
      case List/Cons:
        return xs.head
  else:
    match xs:
      case List/Nil:
        return 0
      case List/Cons:
        return list_get(xs.tail, i - 1)

def list_set(xs, i, value):
  if i == 0:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(value, xs.tail)
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(xs.head, list_set(xs.tail, i - 1, value))

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))

def left_is_matched(target, mtch):
  match mtch:
    case List/Nil:
      return 0
    case List/Cons:
      if mtch.head == target:
        return 1
      else:
        return left_is_matched(target, mtch.tail)

def init_free(i, a, mtch, dist, roots, inf):
  if i == a:
    return (roots, dist)
  else:
    if left_is_matched(i, mtch) == 1:
      return init_free(i + 1, a, mtch, dist, roots, inf)
    else:
      dist2 = list_set(dist, i, 0)
      roots2 = List/Cons(i, roots)
      return init_free(i + 1, a, mtch, dist2, roots2, inf)

def bfs_edges(u, neighbors, back, dist, best, depth, mtch, sentinel, inf):
  match neighbors:
    case List/Nil:
      return (back, dist, best)
    case List/Cons:
      v = neighbors.head
      owner = list_get(mtch, v)
      if owner == sentinel:
        candidate = depth + 1
        if candidate < best:
          return bfs_edges(u, neighbors.tail, back, dist, candidate, depth, mtch, sentinel, inf)
        else:
          return bfs_edges(u, neighbors.tail, back, dist, best, depth, mtch, sentinel, inf)
      else:
        owner_dist = list_get(dist, owner)
        next_depth = depth + 1
        if owner_dist == inf:
          if next_depth < best:
            dist2 = list_set(dist, owner, next_depth)
            back2 = List/Cons(owner, back)
            return bfs_edges(u, neighbors.tail, back2, dist2, best, depth, mtch, sentinel, inf)
          else:
            return bfs_edges(u, neighbors.tail, back, dist, best, depth, mtch, sentinel, inf)
        else:
          return bfs_edges(u, neighbors.tail, back, dist, best, depth, mtch, sentinel, inf)

def bfs_loop(front, back, adj, mtch, dist, best, sentinel, inf):
  match front:
    case List/Nil:
      match back:
        case List/Nil:
          return (dist, best)
        case List/Cons:
          front2 = reverse_list(back, [])
          return bfs_loop(front2, [], adj, mtch, dist, best, sentinel, inf)
    case List/Cons:
      u = front.head
      depth = list_get(dist, u)
      if depth >= best:
        return bfs_loop(front.tail, back, adj, mtch, dist, best, sentinel, inf)
      else:
        neighbors = list_get(adj, u)
        (back2, dist2, best2) = bfs_edges(u, neighbors, back, dist, best, depth, mtch, sentinel, inf)
        return bfs_loop(front.tail, back2, adj, mtch, dist2, best2, sentinel, inf)

def augment_dfs(u, adj, mtch, dist, shortest, sentinel, inf):
  depth = list_get(dist, u)
  if depth >= shortest:
    dist2 = list_set(dist, u, inf)
    return (0, mtch, dist2)
  else:
    neighbors = list_get(adj, u)
    (ok, mtch2, dist2) = dfs_neighbors(u, neighbors, adj, mtch, dist, depth, shortest, sentinel, inf)
    if ok == 1:
      return (1, mtch2, dist2)
    else:
      dist3 = list_set(dist2, u, inf)
      return (0, mtch2, dist3)

def dfs_neighbors(u, neighbors, adj, mtch, dist, depth, shortest, sentinel, inf):
  match neighbors:
    case List/Nil:
      return (0, mtch, dist)
    case List/Cons:
      v = neighbors.head
      owner = list_get(mtch, v)
      if owner == sentinel:
        if depth + 1 == shortest:
          mtch2 = list_set(mtch, v, u)
          return (1, mtch2, dist)
        else:
          return dfs_neighbors(u, neighbors.tail, adj, mtch, dist, depth, shortest, sentinel, inf)
      else:
        owner_depth = list_get(dist, owner)
        if owner_depth == depth + 1:
          (ok, mtch2, dist2) = augment_dfs(owner, adj, mtch, dist, shortest, sentinel, inf)
          if ok == 1:
            mtch3 = list_set(mtch2, v, u)
            return (1, mtch3, dist2)
          else:
            return dfs_neighbors(u, neighbors.tail, adj, mtch2, dist2, depth, shortest, sentinel, inf)
        else:
          return dfs_neighbors(u, neighbors.tail, adj, mtch, dist, depth, shortest, sentinel, inf)

def process_roots(roots, adj, mtch, dist, shortest, sentinel, inf, added):
  match roots:
    case List/Nil:
      return (mtch, dist, added)
    case List/Cons:
      u = roots.head
      (ok, mtch2, dist2) = augment_dfs(u, adj, mtch, dist, shortest, sentinel, inf)
      if ok == 1:
        return process_roots(roots.tail, adj, mtch2, dist2, shortest, sentinel, inf, added + 1)
      else:
        return process_roots(roots.tail, adj, mtch2, dist2, shortest, sentinel, inf, added)

def matching_phases(a, b, adj, mtch, total, sentinel, inf):
  dist = make_list(a, inf)
  (roots, dist2) = init_free(0, a, mtch, dist, [], inf)
  (dist3, shortest) = bfs_loop(roots, [], adj, mtch, dist2, inf, sentinel, inf)
  if shortest == inf:
    return total
  else:
    (mtch2, dist4, added) = process_roots(roots, adj, mtch, dist3, shortest, sentinel, inf, 0)
    if added == 0:
      return total
    else:
      return matching_phases(a, b, adj, mtch2, total + added, sentinel, inf)
