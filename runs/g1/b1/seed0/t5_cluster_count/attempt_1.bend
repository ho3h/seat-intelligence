def prog(x):
  (n, pairs) = x
  parents = make_parents(0, n)
  sizes = make_sizes(0, n)
  return merge_edges(pairs, parents, sizes, n)

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

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return at(xs.tail, i - 1)

def put(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, put(xs.tail, i - 1, value))

def find_root(parents, x):
  p = at(parents, x)
  if p == x:
    return x
  else:
    return find_root(parents, p)

def merge_edges(edges, parents, sizes, count):
  match edges:
    case List/Nil:
      return count
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(parents, u)
      root_v = find_root(parents, v)
      if root_u == root_v:
        return merge_edges(edges.tail, parents, sizes, count)
      else:
        size_u = at(sizes, root_u)
        size_v = at(sizes, root_v)
        if size_u >= size_v:
          new_parents = put(parents, root_v, root_u)
          new_sizes = put(sizes, root_u, size_u + size_v)
          return merge_edges(edges.tail, new_parents, new_sizes, count - 1)
        else:
          new_parents = put(parents, root_u, root_v)
          new_sizes = put(sizes, root_v, size_u + size_v)
          return merge_edges(edges.tail, new_parents, new_sizes, count - 1)
