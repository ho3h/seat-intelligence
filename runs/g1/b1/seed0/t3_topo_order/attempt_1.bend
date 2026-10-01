def prog(x):
  (n, edges) = x
  indegs = make_zeros(n, 0)
  indegs = count_edges(edges, indegs)
  return build_order(n, edges, indegs, 0, [])

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
      next_indegs = increment_at(indegs, v, 0)
      return count_edges(edges.tail, next_indegs)

def increment_at(xs, i, unused):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(xs.head + 1, xs.tail)
      else:
        return List/Cons(xs.head, increment_at(xs.tail, i - 1, unused))

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

def remove_outgoing(edges, vertex, indegs):
  match edges:
    case List/Nil:
      return indegs
    case List/Cons:
      (u, v) = edges.head
      if u == vertex:
        next_indegs = decrement_at(indegs, v)
        return remove_outgoing(edges.tail, vertex, next_indegs)
      else:
        return remove_outgoing(edges.tail, vertex, indegs)

def build_order(n, edges, indegs, count, acc):
  if count == n:
    return reverse_list(acc, [])
  else:
    vertex = find_zero(indegs, 0)
    marked = set_at(indegs, vertex, n)
    next_indegs = remove_outgoing(edges, vertex, marked)
    return build_order(n, edges, next_indegs, count + 1, List/Cons(vertex, acc))

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))
