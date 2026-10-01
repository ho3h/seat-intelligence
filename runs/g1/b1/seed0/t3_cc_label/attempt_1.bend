def prog(x):
  (n, edges) = x
  parents = make_parents(0, n)
  parents2 = union_edges(edges, parents)
  return all_labels(parents2, 0, n)

def make_parents(i, n):
  if i == n:
    return []
  else:
    rest = make_parents(i + 1, n)
    return List/Cons(i, rest)

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
        rest = set_at(xs.tail, i - 1, value)
        return List/Cons(xs.head, rest)

def find_root(parents, x):
  p = get_at(parents, x)
  if p == x:
    return (x, parents)
  else:
    (root, parents2) = find_root(parents, p)
    parents3 = set_at(parents2, x, root)
    return (root, parents3)

def union_edges(edges, parents):
  match edges:
    case List/Nil:
      return parents
    case List/Cons:
      (u, v) = edges.head
      (root_u, parents1) = find_root(parents, u)
      (root_v, parents2) = find_root(parents1, v)
      if root_u == root_v:
        return union_edges(edges.tail, parents2)
      else:
        if root_u < root_v:
          parents3 = set_at(parents2, root_v, root_u)
          return union_edges(edges.tail, parents3)
        else:
          parents3 = set_at(parents2, root_u, root_v)
          return union_edges(edges.tail, parents3)

def all_labels(parents, i, n):
  if i == n:
    return []
  else:
    (root, parents2) = find_root(parents, i)
    rest = all_labels(parents2, i + 1, n)
    return List/Cons(root, rest)
