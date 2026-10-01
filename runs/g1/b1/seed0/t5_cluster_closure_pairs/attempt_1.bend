def prog(x):
  (n, pairs) = x
  parents = make_parents(0, n)
  sizes = make_sizes(0, n)
  (final_parents, final_sizes) = process_edges(pairs, parents, sizes)
  return count_roots(final_parents, final_sizes, 0, n)

def make_parents(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_parents(i + 1, n))

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

def put_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        rest = put_at(xs.tail, i - 1, value)
        return List/Cons(xs.head, rest)

def find_root(parents, node):
  parent = get_at(parents, node)
  if parent == node:
    return node
  else:
    return find_root(parents, parent)

def process_edges(edges, parents, sizes):
  match edges:
    case List/Nil:
      return (parents, sizes)
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(parents, u)
      root_v = find_root(parents, v)
      if root_u == root_v:
        return process_edges(edges.tail, parents, sizes)
      else:
        size_u = get_at(sizes, root_u)
        size_v = get_at(sizes, root_v)
        if size_u < size_v:
          parents2 = put_at(parents, root_u, root_v)
          sizes2 = put_at(sizes, root_v, size_u + size_v)
          return process_edges(edges.tail, parents2, sizes2)
        else:
          parents2 = put_at(parents, root_v, root_u)
          sizes2 = put_at(sizes, root_u, size_u + size_v)
          return process_edges(edges.tail, parents2, sizes2)

def count_roots(parents, sizes, i, n):
  if i == n:
    return 0
  else:
    parent = get_at(parents, i)
    if parent == i:
      size = get_at(sizes, i)
      return size * (size - 1) / 2 + count_roots(parents, sizes, i + 1, n)
    else:
      return count_roots(parents, sizes, i + 1, n)
