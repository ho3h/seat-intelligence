def prog(x):
  (n, edges) = x
  vertices = make_vertices(0, n)
  return search(vertices, edges, 0, 0)

def make_vertices(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_vertices(i + 1, n))

def adjacent(edges, u, v):
  match edges:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = edges.head
      if a == u:
        if b == v:
          return 1
        else:
          if a == v:
            if b == u:
              return 1
            else:
              return adjacent(edges.tail, u, v)
          else:
            return adjacent(edges.tail, u, v)
      else:
        if a == v:
          if b == u:
            return 1
          else:
            return adjacent(edges.tail, u, v)
        else:
          return adjacent(edges.tail, u, v)

def has_neighbor(vertices, edges, v):
  match vertices:
    case List/Nil:
      return 0
    case List/Cons:
      if adjacent(edges, v, vertices.head) == 1:
        return 1
      else:
        return has_neighbor(vertices.tail, edges, v)

def make_class(vertices, edges, chosen, blocked):
  match vertices:
    case List/Nil:
      return (chosen, blocked)
    case List/Cons:
      if has_neighbor(chosen, edges, vertices.head) == 1:
        return make_class(vertices.tail, edges, chosen, List/Cons(vertices.head, blocked))
      else:
        return make_class(vertices.tail, edges, List/Cons(vertices.head, chosen), blocked)

def color_count(vertices, edges, color):
  match vertices:
    case List/Nil:
      return color - 1
    case List/Cons:
      (chosen, blocked) = make_class(vertices, edges, [], [])
      return color_count(blocked, edges, color + 1)

def filter_neighbors(vertices, edges, v):
  match vertices:
    case List/Nil:
      return []
    case List/Cons:
      rest = filter_neighbors(vertices.tail, edges, v)
      if adjacent(edges, v, vertices.head) == 1:
        return List/Cons(vertices.head, rest)
      else:
        return rest

def list_length(vertices):
  match vertices:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(vertices.tail)

def max_value(a, b):
  if a > b:
    return a
  else:
    return b

def search(candidates, edges, size, best):
  if size + list_length(candidates) <= best:
    return best
  else:
    if size + color_count(candidates, edges, 1) <= best:
      return best
    else:
      match candidates:
        case List/Nil:
          return max_value(size, best)
        case List/Cons:
          next_candidates = filter_neighbors(candidates.tail, edges, candidates.head)
          best_with = search(next_candidates, edges, size + 1, best)
          return search(candidates.tail, edges, size, best_with)
