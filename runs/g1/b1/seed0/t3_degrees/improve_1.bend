def prog(x):
  (n, edges) = x
  incidences = make_incidences(edges)
  return degree_tree(incidences, 0, n, [])

def make_incidences(edges):
  match edges:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = edges.head
      rest = make_incidences(edges.tail)
      return List/Cons(u, List/Cons(v, rest))

def partition_incidents(xs, threshold):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = partition_incidents(xs.tail, threshold)
      if xs.head < threshold:
        return (List/Cons(xs.head, left), right)
      else:
        return (left, List/Cons(xs.head, right))

def count_items(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return count_items(xs.tail, acc + 1)

def degree_tree(xs, lo, size, tail):
  if size == 0:
    return tail
  else:
    if size == 1:
      degree = count_items(xs, 0)
      return List/Cons(degree, tail)
    else:
      left_size = size / 2
      right_size = size - left_size
      threshold = lo + left_size
      (left, right) = partition_incidents(xs, threshold)
      right_result = degree_tree(right, threshold, right_size, tail)
      return degree_tree(left, lo, left_size, right_result)
