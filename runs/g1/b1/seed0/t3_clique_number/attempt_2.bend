def prog(x):
  (n, edges) = x
  graph0 = make_rows(n)
  graph = add_edges(edges, graph0, n)
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
  if nth(row, v) == 1:
    return 1
  else:
    return 0

def has_neighbor(vertices, graph, v):
  match vertices:
    case List/Nil:
      return 0
    case List/Cons:
      if adjacent(graph, v, vertices.head) == 1:
        return 1
      else:
        return has_neighbor(vertices.tail, graph, v)

def make_class(vertices, graph, chosen, blocked):
  match vertices:
    case List/Nil:
      return (chosen, blocked)
    case List/Cons:
      if has_neighbor(chosen, graph, vertices.head) == 1:
        return make_class(vertices.tail, graph, chosen, List/Cons(vertices.head, blocked))
      else:
        return make_class(vertices.tail, graph, List/Cons(vertices.head, chosen), blocked)

def color_count(vertices, graph, color):
  match vertices:
    case List/Nil:
      return color - 1
    case List/Cons:
      (chosen, blocked) = make_class(vertices, graph, [], [])
      return color_count(blocked, graph, color + 1)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def filter_neighbors(items, graph, v):
  match items:
    case List/Nil:
      return []
    case List/Cons:
      rest = filter_neighbors(items.tail, graph, v)
      if adjacent(graph, v, items.head) == 1:
        return List/Cons(items.head, rest)
      else:
        return rest

def max_value(a, b):
  if a > b:
    return a
  else:
    return b

def search(candidates, graph, size, best):
  if size + list_length(candidates) <= best:
    return best
  else:
    colors = color_count(candidates, graph, 1)
    if size + colors <= best:
      return best
    else:
      match candidates:
        case List/Nil:
          return max_value(size, best)
        case List/Cons:
          next_candidates = filter_neighbors(candidates.tail, graph, candidates.head)
          best1 = search(next_candidates, graph, size + 1, best)
          return search(candidates.tail, graph, size, best1)
