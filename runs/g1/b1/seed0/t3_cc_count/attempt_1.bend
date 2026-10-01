def prog(x):
  (n, edges) = x
  return count_vertices(0, n, edges, [], 0)

def count_vertices(i, n, edges, seen, components):
  if i == n:
    return components
  else:
    if contains(i, seen):
      return count_vertices(i + 1, n, edges, seen, components)
    else:
      seen2 = flood(i, edges, List/Cons(i, seen))
      return count_vertices(i + 1, n, edges, seen2, components + 1)

def contains(target, xs):
  match xs:
    case List/Nil:
      return false
    case List/Cons:
      if xs.head == target:
        return true
      else:
        return contains(target, xs.tail)

def flood(v, edges, seen):
  return scan_edges(v, edges, seen)

def scan_edges(v, edges, seen):
  match edges:
    case List/Nil:
      return seen
    case List/Cons:
      (a, b) = edges.head
      if a == v:
        if contains(b, seen):
          return scan_edges(v, edges.tail, seen)
        else:
          seen2 = flood(b, edges, List/Cons(b, seen))
          return scan_edges(v, edges.tail, seen2)
      else:
        if b == v:
          if contains(a, seen):
            return scan_edges(v, edges.tail, seen)
          else:
            seen2 = flood(a, edges, List/Cons(a, seen))
            return scan_edges(v, edges.tail, seen2)
        else:
          return scan_edges(v, edges.tail, seen)
