def prog(x):
  (n, edges) = x
  return count_vertices(0, n, edges, [], 0)

def count_vertices(i, n, edges, seen, components):
  if i == n:
    return components
  else:
    if contains(i, seen) == 1:
      return count_vertices(i + 1, n, edges, seen, components)
    else:
      seen2 = closure(edges, List/Cons(i, seen))
      return count_vertices(i + 1, n, edges, seen2, components + 1)

def closure(edges, seen):
  seen2 = scan_edges(edges, seen)
  if size(seen2) == size(seen):
    return seen2
  else:
    return closure(edges, seen2)

def scan_edges(edges, seen):
  match edges:
    case List/Nil:
      return seen
    case List/Cons:
      (a, b) = edges.head
      seen1 = add_if_connected(a, b, seen)
      seen2 = add_if_connected(b, a, seen1)
      return scan_edges(edges.tail, seen2)

def add_if_connected(a, b, seen):
  if contains(a, seen) == 1:
    if contains(b, seen) == 1:
      return seen
    else:
      return List/Cons(b, seen)
  else:
    return seen

def contains(target, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == target:
        return 1
      else:
        return contains(target, xs.tail)

def size(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + size(xs.tail)
