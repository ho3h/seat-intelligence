def prog(x):
  (n, s, k, edges) = x
  initial = List/Cons(s, List/Nil)
  reached = bfs(edges, initial, initial, k)
  return count(reached)

def contains(xs, target):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == target:
        return 1
      else:
        return contains(xs.tail, target)

def add_candidate(v, seen, nxt):
  if contains(seen, v) == 1:
    return nxt
  else:
    if contains(nxt, v) == 1:
      return nxt
    else:
      return List/Cons(v, nxt)

def scan_edges(edges, frontier, seen, nxt):
  match edges:
    case List/Nil:
      return nxt
    case List/Cons:
      (u, v) = edges.head
      if contains(frontier, u) == 1:
        nxt1 = add_candidate(v, seen, nxt)
      else:
        nxt1 = nxt
      if contains(frontier, v) == 1:
        nxt2 = add_candidate(u, seen, nxt1)
      else:
        nxt2 = nxt1
      return scan_edges(edges.tail, frontier, seen, nxt2)

def concat(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, concat(xs.tail, ys))

def bfs(edges, frontier, seen, remaining):
  if remaining == 0:
    return seen
  else:
    match frontier:
      case List/Nil:
        return seen
      case List/Cons:
        nxt = scan_edges(edges, frontier, seen, List/Nil)
        match nxt:
          case List/Nil:
            return seen
          case List/Cons:
            all_seen = concat(nxt, seen)
            return bfs(edges, nxt, all_seen, remaining - 1)

def count(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + count(xs.tail)
