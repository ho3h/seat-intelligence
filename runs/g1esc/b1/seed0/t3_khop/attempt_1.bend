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
        nf = next_frontier(frontier, edges, visited, List/Nil)
        new_visited = append_list(nf, visited)
        return bfs(nf, new_visited, edges, k-1)

def next_frontier(frontier, edges, visited, acc):
  match frontier:
    case List/Nil:
      return acc
    case List/Cons:
      nbrs = neighbors(frontier.head, edges, List/Nil)
      acc2 = add_unvisited(nbrs, visited, acc)
      return next_frontier(frontier.tail, edges, visited, acc2)

def add_unvisited(ns, visited, acc):
  match ns:
    case List/Nil:
      return acc
    case List/Cons:
      w = ns.head
      if contains(visited, w) == 0:
        if contains(acc, w) == 0:
          return add_unvisited(ns.tail, visited, List/Cons(w, acc))
        else:
          return add_unvisited(ns.tail, visited, acc)
      else:
        return add_unvisited(ns.tail, visited, acc)

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

def append_list(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append_list(xs.tail, ys))
