def prog(x):
  (n, s, k, edges) = x
  return bfs(List/Cons(s, List/Nil), List/Cons(s, List/Nil), edges, k)

def bfs(frontier, visited, edges, k):
  if k == 0:
    return length(visited)
  else:
    match frontier:
      case List/Nil:
        return length(visited)
      case List/Cons:
        (new_frontier, new_visited) = process_frontier(frontier, edges, visited, List/Nil)
        return bfs(new_frontier, new_visited, edges, k - 1)

def process_frontier(frontier, edges, visited, acc_frontier):
  match frontier:
    case List/Nil:
      return (acc_frontier, visited)
    case List/Cons:
      u = frontier.head
      nbrs = neighbors(u, edges, List/Nil)
      (acc_frontier2, visited2) = add_neighbors(nbrs, visited, acc_frontier)
      return process_frontier(frontier.tail, edges, visited2, acc_frontier2)

def add_neighbors(ns, visited, acc_frontier):
  match ns:
    case List/Nil:
      return (acc_frontier, visited)
    case List/Cons:
      w = ns.head
      if contains(visited, w) == 0:
        return add_neighbors(ns.tail, List/Cons(w, visited), List/Cons(w, acc_frontier))
      else:
        return add_neighbors(ns.tail, visited, acc_frontier)

def neighbors(u, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (a, b) = edges.head
      if a == u:
        return neighbors(u, edges.tail, List/Cons(b, acc))
      else:
        if b == u:
          return neighbors(u, edges.tail, List/Cons(a, acc))
        else:
          return neighbors(u, edges.tail, acc)

def contains(xs, x):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == x:
        return 1
      else:
        return contains(xs.tail, x)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)
