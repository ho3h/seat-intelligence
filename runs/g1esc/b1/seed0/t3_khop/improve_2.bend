def prog(x):
  (n, s, k, edges) = x
  return bfs(List/Cons(s, List/Nil), List/Cons(s, List/Nil), edges, k, 1)

def bfs(frontier, visited, edges, k, count):
  if k == 0:
    return count
  else:
    match frontier:
      case List/Nil:
        return count
      case List/Cons:
        (new_frontier, new_visited, new_count) = process_frontier(frontier, edges, visited, List/Nil, count)
        return bfs(new_frontier, new_visited, edges, k - 1, new_count)

def process_frontier(frontier, edges, visited, acc_frontier, count):
  match frontier:
    case List/Nil:
      return (acc_frontier, visited, count)
    case List/Cons:
      (visited2, acc_frontier2, count2) = scan_edges_add(frontier.head, edges, visited, acc_frontier, count)
      return process_frontier(frontier.tail, edges, visited2, acc_frontier2, count2)

def scan_edges_add(u, edges, visited, acc_frontier, count):
  match edges:
    case List/Nil:
      return (visited, acc_frontier, count)
    case List/Cons:
      (a, b) = edges.head
      if a == u:
        return scan_edges_add(u, edges.tail, maybe_add(b, visited, acc_frontier, count))
      else:
        if b == u:
          return scan_edges_add(u, edges.tail, maybe_add(a, visited, acc_frontier, count))
        else:
          return scan_edges_add(u, edges.tail, visited, acc_frontier, count)

def maybe_add(w, visited, acc_frontier, count):
  if contains(visited, w) == 0:
    return (List/Cons(w, visited), List/Cons(w, acc_frontier), count + 1)
  else:
    return (visited, acc_frontier, count)

def contains(xs, x):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == x:
        return 1
      else:
        return contains(xs.tail, x)
