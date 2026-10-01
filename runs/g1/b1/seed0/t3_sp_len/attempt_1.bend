def prog(x):
  (n, s, t, edges) = x
  if s == t:
    return 0
  else:
    return bfs([s], [s], edges, t, 0)

def bfs(frontier, visited, edges, t, depth):
  match frontier:
    case List/Nil:
      return 16777215
    case List/Cons:
      (next_frontier, next_visited, found) = expand_frontier(frontier, [], visited, edges, t)
      if found == 1:
        return depth + 1
      else:
        return bfs(next_frontier, next_visited, edges, t, depth + 1)

def expand_frontier(frontier, next_frontier, visited, edges, t):
  match frontier:
    case List/Nil:
      return (next_frontier, visited, 0)
    case List/Cons:
      (next2, visited2, found1) = scan_edges(edges, frontier.head, next_frontier, visited, t, 0)
      (next3, visited3, found2) = expand_frontier(frontier.tail, next2, visited2, edges, t)
      return (next3, visited3, found1 | found2)

def scan_edges(edges, src, next_frontier, visited, t, found):
  match edges:
    case List/Nil:
      return (next_frontier, visited, found)
    case List/Cons:
      (u, v) = edges.head
      if u == src:
        (next2, visited2, found2) = add_neighbor(v, next_frontier, visited, t, found)
        return scan_edges(edges.tail, src, next2, visited2, t, found2)
      else:
        if v == src:
          (next2, visited2, found2) = add_neighbor(u, next_frontier, visited, t, found)
          return scan_edges(edges.tail, src, next2, visited2, t, found2)
        else:
          return scan_edges(edges.tail, src, next_frontier, visited, t, found)

def add_neighbor(v, next_frontier, visited, t, found):
  if v == t:
    found2 = 1
  else:
    found2 = found
  if contains(visited, v) == 0:
    return (List/Cons(v, next_frontier), List/Cons(v, visited), found2)
  else:
    return (next_frontier, visited, found2)

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)
