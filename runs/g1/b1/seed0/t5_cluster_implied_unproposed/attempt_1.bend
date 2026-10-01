def make_zeros(n, i):
  if i == n:
    return []
  else:
    return List/Cons(0, make_zeros(n, i + 1))

def make_matrix(n, i):
  if i == n:
    return []
  else:
    row = make_zeros(n, 0)
    return List/Cons(row, make_matrix(n, i + 1))

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
        return List/Cons(xs.head, put_at(xs.tail, i - 1, value))

def find_root(parents, node):
  parent = get_at(parents, node)
  if parent == node:
    return node
  else:
    return find_root(parents, parent)

def process_edges(edges, parents, seen, distinct):
  match edges:
    case List/Nil:
      return (parents, seen, distinct)
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(parents, u)
      root_v = find_root(parents, v)
      if root_u == root_v:
        parents2 = parents
      else:
        parents2 = put_at(parents, root_u, root_v)
      row = get_at(seen, u)
      present = get_at(row, v)
      if present == 0:
        row2 = put_at(row, v, 1)
        seen2 = put_at(seen, u, row2)
        return process_edges(edges.tail, parents2, seen2, distinct + 1)
      else:
        return process_edges(edges.tail, parents2, seen, distinct)

def add_sizes(parents, i, sizes, n):
  if i == n:
    return sizes
  else:
    root = find_root(parents, i)
    old_size = get_at(sizes, root)
    sizes2 = put_at(sizes, root, old_size + 1)
    return add_sizes(parents, i + 1, sizes2, n)

def sum_cluster_pairs(sizes, i, n, total):
  if i == n:
    return total
  else:
    size = get_at(sizes, i)
    if size > 1:
      total2 = total + (size * (size - 1)) / 2
      return sum_cluster_pairs(sizes, i + 1, n, total2)
    else:
      return sum_cluster_pairs(sizes, i + 1, n, total)

def prog(x):
  (n, pairs) = x
  parents = make_zeros(n, 0)
  parents2 = make_parents(n, 0)
  seen = make_matrix(n, 0)
  (merged, seen2, distinct) = process_edges(pairs, parents2, seen, 0)
  sizes = make_zeros(n, 0)
  sizes2 = add_sizes(merged, 0, sizes, n)
  total = sum_cluster_pairs(sizes2, 0, n, 0)
  return total - distinct

def make_parents(n, i):
  if i == n:
    return []
  else:
    return List/Cons(i, make_parents(n, i + 1))
