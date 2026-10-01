def prog(x):
  (clusters, edges) = x
  rows = empty_rows(clusters)
  rows = process_edges(edges, clusters, rows)
  return build_output(clusters, rows, 0)

def empty_rows(clusters):
  match clusters:
    case List/Nil:
      return []
    case List/Cons:
      return List/Cons([], empty_rows(clusters.tail))

def process_edges(edges, clusters, rows):
  match edges:
    case List/Nil:
      return rows
    case List/Cons:
      (u, v) = edges.head
      a = lookup(clusters, u)
      b = lookup(clusters, v)
      if a == b:
        return process_edges(edges.tail, clusters, rows)
      else:
        updated = update_rows(rows, 0, a, b)
        return process_edges(edges.tail, clusters, updated)

def update_rows(rows, index, a, b):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      if index == a:
        return List/Cons(insert_neighbor(rows.head, b), update_rows(rows.tail, index + 1, a, b))
      else:
        if index == b:
          return List/Cons(insert_neighbor(rows.head, a), update_rows(rows.tail, index + 1, a, b))
        else:
          return List/Cons(rows.head, update_rows(rows.tail, index + 1, a, b))

def insert_neighbor(neighbors, value):
  if contains(neighbors, value) == 1:
    return neighbors
  else:
    return List/Cons(value, neighbors)

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def build_output(clusters, rows, index):
  match clusters:
    case List/Nil:
      return []
    case List/Cons:
      match rows:
        case List/Nil:
          return []
        case List/Cons:
          rest = build_output(clusters.tail, rows.tail, index + 1)
          if clusters.head == index:
            return List/Cons(count_list(rows.head), rest)
          else:
            return rest

def count_list(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + count_list(xs.tail)

def lookup(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return lookup(xs.tail, index - 1)
