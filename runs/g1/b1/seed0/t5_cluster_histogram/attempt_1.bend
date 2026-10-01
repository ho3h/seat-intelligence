def prog(x):
  (n, pairs) = x
  parent = make_parent(0, n)
  sizes = make_sizes(0, n)
  (parent2, sizes2) = union_all(pairs, parent, sizes)
  return count_roots(parent2, sizes2, 0, n, [0, 0, 0, 0, 0, 0, 0, 0])

def make_parent(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_parent(i + 1, n))

def make_sizes(i, n):
  if i == n:
    return []
  else:
    return List/Cons(1, make_sizes(i + 1, n))

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

def find_root(parent, node):
  p = get_at(parent, node)
  if p == node:
    return node
  else:
    return find_root(parent, p)

def union_all(edges, parent, sizes):
  match edges:
    case List/Nil:
      return (parent, sizes)
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(parent, u)
      root_v = find_root(parent, v)
      if root_u == root_v:
        return union_all(edges.tail, parent, sizes)
      else:
        size_u = get_at(sizes, root_u)
        size_v = get_at(sizes, root_v)
        if size_u < size_v:
          parent2 = set_at(parent, root_u, root_v)
          sizes2 = set_at(sizes, root_v, size_u + size_v)
          return union_all(edges.tail, parent2, sizes2)
        else:
          parent2 = set_at(parent, root_v, root_u)
          sizes2 = set_at(sizes, root_u, size_u + size_v)
          return union_all(edges.tail, parent2, sizes2)

def increment_at(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(xs.head + 1, xs.tail)
      else:
        return List/Cons(xs.head, increment_at(xs.tail, i - 1))

def count_roots(parent, sizes, i, n, hist):
  if i == n:
    return hist
  else:
    p = get_at(parent, i)
    if p == i:
      component_size = get_at(sizes, i)
      if component_size >= 8:
        bin = 7
      else:
        bin = component_size - 1
      hist2 = increment_at(hist, bin)
      return count_roots(parent, sizes, i + 1, n, hist2)
    else:
      return count_roots(parent, sizes, i + 1, n, hist)
