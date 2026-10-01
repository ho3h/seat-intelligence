def prog(x):
  (n, s, k, edges) = x
  return bfs(edges, List/Cons(s, List/Nil), List/Cons(s, List/Nil), k)

def contains(xs, target):
  match xs:
    case List/Nil:
      return false
    case List/Cons:
      if xs.head == target:
        return true
      else:
        return contains(xs.tail, target)

def length(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return length(xs.tail, acc + 1)

def add_if_new(candidate, edges, frontier, seen, next):
  if contains(seen, candidate):
    return scan_edges(edges, frontier, seen, next)
  else:
    return scan_edges(
      edges,
      frontier,
      List/Cons(candidate, seen),
      List/Cons(candidate, next)
    )

def scan_edges(edges, frontier, seen, next):
  match edges:
    case List/Nil:
      return (next, seen)
    case List/Cons:
      (u, v) = edges.head
      if contains(frontier, u):
        return add_if_new(v, edges.tail, frontier, seen, next)
      else:
        if contains(frontier, v):
          return add_if_new(u, edges.tail, frontier, seen, next)
        else:
          return scan_edges(edges.tail, frontier, seen, next)

def bfs(edges, frontier, seen, steps):
  if steps == 0:
    return length(seen, 0)
  else:
    (next, next_seen) = scan_edges(edges, frontier, seen, List/Nil)
    match next:
      case List/Nil:
        return length(next_seen, 0)
      case List/Cons:
        return bfs(edges, next, next_seen, steps - 1)
