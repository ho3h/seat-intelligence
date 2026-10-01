def prog(x):
  (n, r, edges) = x
  adj = make_empty(n)
  adj2 = build_adj(edges, adj)
  parents = make_filled(n, 16777215)
  return walk_tree(r, 16777215, adj2, parents)

def make_empty(n):
  if n == 0:
    return []
  else:
    return List/Cons([], make_empty(n - 1))

def make_filled(n, value):
  if n == 0:
    return []
  else:
    return List/Cons(value, make_filled(n - 1, value))

def prepend_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(List/Cons(value, xs.head), xs.tail)
      else:
        return List/Cons(xs.head, prepend_at(xs.tail, i - 1, value))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def replace_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, replace_at(xs.tail, i - 1, value))

def build_adj(edges, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = prepend_at(adj, u, v)
      adj2 = prepend_at(adj1, v, u)
      return build_adj(edges.tail, adj2)

def walk_tree(u, p, adj, parents):
  neighbors = get_at(adj, u)
  return walk_neighbors(neighbors, u, p, adj, parents)

def walk_neighbors(neighbors, u, p, adj, parents):
  match neighbors:
    case List/Nil:
      return parents
    case List/Cons:
      v = neighbors.head
      if v == p:
        return walk_neighbors(neighbors.tail, u, p, adj, parents)
      else:
        parents1 = replace_at(parents, v, u)
        parents2 = walk_tree(v, u, adj, parents1)
        return walk_neighbors(neighbors.tail, u, p, adj, parents2)
