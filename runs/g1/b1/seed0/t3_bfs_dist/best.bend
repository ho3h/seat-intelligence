def prog(x):
  (n, s, edges) = x
  initial = make_distances(n)
  initial2 = dist_put(initial, s, 0)
  return relax_rounds(edges, initial2, n)

def make_distances(n):
  if n == 0:
    return []
  else:
    tail = make_distances(n - 1)
    return List/Cons(16777215, tail)

def dist_at(xs, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return dist_at(xs.tail, i - 1)

def dist_put(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        tail2 = dist_put(xs.tail, i - 1, value)
        return List/Cons(xs.head, tail2)

def relax_edges(edges, distances):
  match edges:
    case List/Nil:
      return distances
    case List/Cons:
      (u, v) = edges.head
      du = dist_at(distances, u)
      dv = dist_at(distances, v)
      if du != 16777215:
        candidate = du + 1
        if candidate < dv:
          distances2 = dist_put(distances, v, candidate)
        else:
          distances2 = distances
      else:
        distances2 = distances
      return relax_edges(edges.tail, distances2)

def relax_rounds(edges, distances, rounds):
  if rounds == 0:
    return distances
  else:
    distances2 = relax_edges(edges, distances)
    return relax_rounds(edges, distances2, rounds - 1)
