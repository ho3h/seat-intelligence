def prog(x):
  (n, edges) = x
  indegs = make_zeros(n, 0)
  indegs = count_edges(edges, indegs)
  adj = build_adj(0, n, edges)
  return build_order(n, adj, indegs, 0, [])

def make_zeros(n, i):
  if i == n:
    return []
  else:
    return List/Cons(0, make_zeros(n, i + 1))

def count_edges(edges, indegs):
  match edges:
    case List/Nil:
      return indegs
    case List/Cons:
      (u, v) = edges.head
      next_indegs = increment_at(indegs, v)
      return count_edges(edges.tail, next_indegs)

def increment_at(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(xs.head + 1, xs.tail)
      else:
        return List/Cons(xs.head, increment_at(xs.tail, i - 1))

def split_edges(edges, mid, left, right):
  match edges:
    case List/Nil:
      return (left, right)
    case List/Cons:
      (u, v) = edges.head
      if u < mid:
        return split_edges(edges.tail, mid, List/Cons(edges.head, left), right)
      else:
        return split_edges(edges.tail, mid, left, List/Cons(edges.head, right))

def destinations(edges):
  match edges:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = edges.head
      return List/Cons(v, destinations(edges.tail))

def build_adj(lo, hi, edges):
  if lo == hi:
    return []
  else:
    if lo + 1 == hi:
      return List/Cons(destinations(edges), [])
    else:
      mid = (lo + hi) / 2
      (left_edges, right_edges) = split_edges(edges, mid, [], [])
      left_adj = build_adj(lo, mid, left_edges)
      right_adj = build_adj(mid, hi, right_edges)
      return concat(left_adj, right_adj)

def concat(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, concat(xs.tail, ys))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def find_zero(xs, i):
  match xs:
    case List/Nil:
      return i
    case List/Cons:
      if xs.head == 0:
        return i
      else:
        return find_zero(xs.tail, i + 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def decrement_at(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(xs.head - 1, xs.tail)
      else:
        return List/Cons(xs.head, decrement_at(xs.tail, i - 1))

def decrement_neighbors(neighbors, indegs):
  match neighbors:
    case List/Nil:
      return indegs
    case List/Cons:
      next_indegs = decrement_at(indegs, neighbors.head)
      return decrement_neighbors(neighbors.tail, next_indegs)

def build_order(n, adj, indegs, count, acc):
  if count == n:
    return reverse_list(acc, [])
  else:
    vertex = find_zero(indegs, 0)
    marked = set_at(indegs, vertex, n)
    neighbors = get_at(adj, vertex)
    next_indegs = decrement_neighbors(neighbors, marked)
    return build_order(n, adj, next_indegs, count + 1, List/Cons(vertex, acc))

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))
