def prog(x):
  (n, edges) = x
  return degrees(n, edges, 0)

def degrees(n, edges, v):
  if v == n:
    return []
  else:
    d = count_degree(edges, v, 0)
    rest = degrees(n, edges, v + 1)
    return List/Cons(d, rest)

def count_degree(edges, v, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, w) = edges.head
      if u == v:
        return count_degree(edges.tail, v, acc + 1)
      else:
        if w == v:
          return count_degree(edges.tail, v, acc + 1)
        else:
          return count_degree(edges.tail, v, acc)
