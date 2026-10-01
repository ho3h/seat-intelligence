def prog(x):
  (n, pairs) = x
  labels = make_labels(0, n)
  return solve(pairs, labels)

def make_labels(i, n):
  if i < n:
    return List/Cons(i, make_labels(i + 1, n))
  else:
    return []

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

def label_edges(pairs, labels):
  match pairs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = pairs.head
      ru = get_at(labels, u)
      rv = get_at(labels, v)
      edge = ((u, v), (ru, rv))
      return List/Cons(edge, label_edges(pairs.tail, labels))

def best_neighbor(edges, i, best):
  match edges:
    case List/Nil:
      return best
    case List/Cons:
      (ends, roots) = edges.head
      (u, v) = ends
      (ru, rv) = roots
      if u == i:
        if rv < best:
          return best_neighbor(edges.tail, i, rv)
        else:
          return best_neighbor(edges.tail, i, best)
      else:
        if v == i:
          if ru < best:
            return best_neighbor(edges.tail, i, ru)
          else:
            return best_neighbor(edges.tail, i, best)
        else:
          return best_neighbor(edges.tail, i, best)

def hook_nodes(labels, edges, i):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      best = best_neighbor(edges, i, labels.head)
      return List/Cons(best, hook_nodes(labels.tail, edges, i + 1))

def compress_once(labels):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      parent = get_at(labels, labels.head)
      return List/Cons(parent, compress_once(labels.tail))

def compress_until_stable(labels):
  jumped = compress_once(labels)
  if list_diff(labels, jumped) == 0:
    return jumped
  else:
    return compress_until_stable(jumped)

def solve(pairs, labels):
  edges = label_edges(pairs, labels)
  hooked = hook_nodes(labels, edges, 0)
  compressed = compress_until_stable(hooked)
  if list_diff(labels, compressed) == 0:
    return compressed
  else:
    return solve(pairs, compressed)
