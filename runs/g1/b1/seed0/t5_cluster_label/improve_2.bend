def prog(x):
  (n, pairs) = x
  labels = make_labels(0, n)
  adjacency = make_adjacency(0, n, pairs)
  return solve(labels, adjacency)

def make_labels(i, n):
  if i < n:
    return List/Cons(i, make_labels(i + 1, n))
  else:
    return []

def make_adjacency(i, n, pairs):
  if i < n:
    neighbors = find_neighbors(pairs, i)
    return List/Cons(neighbors, make_adjacency(i + 1, n, pairs))
  else:
    return []

def find_neighbors(pairs, i):
  match pairs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = pairs.head
      rest = find_neighbors(pairs.tail, i)
      if u == i:
        return List/Cons(v, rest)
      else:
        if v == i:
          return List/Cons(u, rest)
        else:
          return rest

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      switch i:
        case 0:
          return xs.head
        case _:
          return get_at(xs.tail, i - 1)

def best_neighbor(neighbors, labels, best):
  match neighbors:
    case List/Nil:
      return best
    case List/Cons:
      neighbor_label = get_at(labels, neighbors.head)
      if neighbor_label < best:
        return best_neighbor(neighbors.tail, labels, neighbor_label)
      else:
        return best_neighbor(neighbors.tail, labels, best)

def hook_nodes(labels, adjacency):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      match adjacency:
        case List/Nil:
          return []
        case List/Cons:
          best = best_neighbor(adjacency.head, labels, labels.head)
          return List/Cons(best, hook_nodes(labels.tail, adjacency.tail))

def compress_once(labels):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      parent = get_at(labels, labels.head)
      return List/Cons(parent, compress_once(labels.tail))

def list_diff(xs, ys):
  match xs:
    case List/Nil:
      match ys:
        case List/Nil:
          return 0
        case List/Cons:
          return 1
    case List/Cons:
      match ys:
        case List/Nil:
          return 1
        case List/Cons:
          if xs.head == ys.head:
            return list_diff(xs.tail, ys.tail)
          else:
            return 1

def compress_until_stable(labels):
  compressed = compress_once(labels)
  if list_diff(labels, compressed) == 0:
    return compressed
  else:
    return compress_until_stable(compressed)

def solve(labels, adjacency):
  hooked = hook_nodes(labels, adjacency)
  compressed = compress_until_stable(hooked)
  if list_diff(labels, compressed) == 0:
    return compressed
  else:
    return solve(compressed, adjacency)
