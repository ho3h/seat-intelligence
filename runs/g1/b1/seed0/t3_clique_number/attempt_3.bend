def prog(x):
  (n, edges) = x
  graph = add_edges(edges, make_rows(n), n)
  vertices = make_vertices(0, n)
  return search(vertices, graph, 0, 0)

def make_zeros(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, make_zeros(n - 1))

def make_rows(n):
  if n == 0:
    return []
  else:
    return List/Cons(make_zeros(n), make_rows(n - 1))

def make_vertices(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_vertices(i + 1, n))

def nth(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return nth(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def set_edge(graph, u, v):
  row = nth(graph, u)
  new_row = set_at(row, v, 1)
  return set_at(graph, u, new_row)

def add_edges(edges, graph, n):
  match edges:
    case List/Nil:
      return graph
    case List/Cons:
      (u, v) = edges.head
      if u < n:
        if v < n:
          graph1 = set_edge(graph, u, v)
          graph2 = set_edge(graph1, v, u)
          return add_edges(edges.tail, graph2, n)
        else:
          return add_edges(edges.tail, graph, n)
      else:
        return add_edges(edges.tail, graph, n)

def adjacent(graph, u, v):
  row = nth(graph, u)
  return nth(row, v)

def filter_neighbors(vertices, graph, v):
  match vertices:
    case List/Nil:
      return []
    case List/Cons:
      rest = filter_neighbors(vertices.tail, graph, v)
      if adjacent(graph, v, vertices.head) == 1:
        return List/Cons(vertices.head, rest)
      else:
        return rest

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def max_value(a, b):
  if a > b:
    return a
  else:
    return b

def search(candidates, graph, size, best):
  if size + list_length(candidates) <= best:
    return best
  else:
    match candidates:
      case List/Nil:
        return max_value(size, best)
      case List/Cons:
        next_candidates = filter_neighbors(candidates.tail, graph, candidates.head)
        best_with = search(next_candidates, graph, size + 1, best)
        return search(candidates.tail, graph, size, best_with)
