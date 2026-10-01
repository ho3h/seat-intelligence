def prog(x):
  (n, pairs) = x
  parents = make_labels(n, 0)
  sizes = make_sizes(n, 0)
  if n == 0:
    return process_edges(pairs, parents, sizes, 0)
  else:
    return process_edges(pairs, parents, sizes, 1)

def make_labels(n, i):
  if i == n:
    return []
  else:
    return List/Cons(i, make_labels(n, i + 1))

def make_sizes(n, i):
  if i == n:
    return []
  else:
    return List/Cons(1, make_sizes(n, i + 1))

def get_at(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return get_at(xs.tail, index - 1)

def set_at(xs, index, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, index - 1, value))

def find_root(parents, node):
  parent = get_at(parents, node)
  if parent == node:
    return node
  else:
    return find_root(parents, parent)

def process_edges(pairs, parents, sizes, best):
  match pairs:
    case List/Nil:
      return best
    case List/Cons:
      (u, v) = pairs.head
      root_u = find_root(parents, u)
      root_v = find_root(parents, v)
      if root_u == root_v:
        return process_edges(pairs.tail, parents, sizes, best)
      else:
        size_u = get_at(sizes, root_u)
        size_v = get_at(sizes, root_v)
        if size_u >= size_v:
          new_size = size_u + size_v
          new_parents = set_at(parents, root_v, root_u)
          new_sizes = set_at(sizes, root_u, new_size)
          if new_size > best:
            return process_edges(pairs.tail, new_parents, new_sizes, new_size)
          else:
            return process_edges(pairs.tail, new_parents, new_sizes, best)
        else:
          new_size = size_u + size_v
          new_parents = set_at(parents, root_u, root_v)
          new_sizes = set_at(sizes, root_v, new_size)
          if new_size > best:
            return process_edges(pairs.tail, new_parents, new_sizes, new_size)
          else:
            return process_edges(pairs.tail, new_parents, new_sizes, best)
