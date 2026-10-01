def prog(x):
  (n, edges) = x
  adj = build_adjacency(0, n, edges)
  return all_eccentricities(0, n, adj)

def build_adjacency(i, n, edges):
  if i == n:
    return []
  else:
    neighbors = find_neighbors(i, edges, [])
    rest = build_adjacency(i + 1, n, edges)
    return List/Cons(neighbors, rest)

def find_neighbors(i, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      if u == i:
        acc1 = List/Cons(v, acc)
      else:
        acc1 = acc
      if v == i:
        acc2 = List/Cons(u, acc1)
      else:
        acc2 = acc1
      return find_neighbors(i, edges.tail, acc2)

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def nth(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return nth(xs.tail, i - 1)

def expand_neighbors(neighbors, visited, next_frontier):
  match neighbors:
    case List/Nil:
      return (visited, next_frontier)
    case List/Cons:
      value = neighbors.head
      if contains(visited, value) == 0:
        visited2 = List/Cons(value, visited)
        next2 = List/Cons(value, next_frontier)
      else:
        visited2 = visited
        next2 = next_frontier
      return expand_neighbors(neighbors.tail, visited2, next2)

def expand_frontier(frontier, adj, visited, next_frontier):
  match frontier:
    case List/Nil:
      return (visited, next_frontier)
    case List/Cons:
      neighbors = nth(adj, frontier.head)
      (visited2, next2) = expand_neighbors(neighbors, visited, next_frontier)
      return expand_frontier(frontier.tail, adj, visited2, next2)

def bfs_eccentricity(adj, frontier, visited, level):
  (visited2, next_frontier) = expand_frontier(frontier, adj, visited, [])
  match next_frontier:
    case List/Nil:
      return level
    case List/Cons:
      return bfs_eccentricity(adj, next_frontier, visited2, level + 1)

def all_eccentricities(i, n, adj):
  if i == n:
    return []
  else:
    start = List/Cons(i, [])
    eccentricity = bfs_eccentricity(adj, start, start, 0)
    rest = all_eccentricities(i + 1, n, adj)
    return List/Cons(eccentricity, rest)
