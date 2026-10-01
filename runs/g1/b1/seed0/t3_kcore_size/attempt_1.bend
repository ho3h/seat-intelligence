def prog(x):
  (n, k, edges) = x
  vertices = make_vertices(n, 0)
  return stabilize(vertices, edges, k)

def make_vertices(n, i):
  if i == n:
    return []
  else:
    return List/Cons(i, make_vertices(n, i + 1))

def contains(x, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == x:
        return 1
      else:
        return contains(x, xs.tail)

def degree(v, edges, active, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (a, b) = edges.head
      if a == v:
        if contains(b, active) == 1:
          return degree(v, edges.tail, active, acc + 1)
        else:
          return degree(v, edges.tail, active, acc)
      else:
        if b == v:
          if contains(a, active) == 1:
            return degree(v, edges.tail, active, acc + 1)
          else:
            return degree(v, edges.tail, active, acc)
        else:
          return degree(v, edges.tail, active, acc)

def filter_core(vertices, edges, k, active):
  match vertices:
    case List/Nil:
      return []
    case List/Cons:
      d = degree(vertices.head, edges, active, 0)
      rest = filter_core(vertices.tail, edges, k, active)
      if d >= k:
        return List/Cons(vertices.head, rest)
      else:
        return rest

def list_length(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return list_length(xs.tail, acc + 1)

def stabilize(active, edges, k):
  next = filter_core(active, edges, k, active)
  if list_length(next, 0) == list_length(active, 0):
    return list_length(next, 0)
  else:
    return stabilize(next, edges, k)
