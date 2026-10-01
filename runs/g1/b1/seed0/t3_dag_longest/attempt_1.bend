def prog(x):
  (n, edges) = x
  distances = make_zeros(n)
  distances = relax_rounds(edges, distances, n)
  return find_max(distances, 0)

def make_zeros(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(0, make_zeros(n - 1))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def relax_edges(edges, distances, changed):
  match edges:
    case List/Nil:
      return (distances, changed)
    case List/Cons:
      (u, v) = edges.head
      from_dist = get_at(distances, u)
      to_dist = get_at(distances, v)
      if from_dist + 1 > to_dist:
        next_distances = set_at(distances, v, from_dist + 1)
        return relax_edges(edges.tail, next_distances, 1)
      else:
        return relax_edges(edges.tail, distances, changed)

def relax_rounds(edges, distances, rounds):
  switch rounds:
    case 0:
      return distances
    case _:
      (next_distances, changed) = relax_edges(edges, distances, 0)
      if changed == 0:
        return next_distances
      else:
        return relax_rounds(edges, next_distances, rounds - 1)

def find_max(xs, current_max):
  match xs:
    case List/Nil:
      return current_max
    case List/Cons:
      if xs.head > current_max:
        return find_max(xs.tail, xs.head)
      else:
        return find_max(xs.tail, current_max)
