def prog(x):
  (n, r, edges) = x
  adj = make_empty(n)
  adj2 = build_adj(edges, adj)
  parents = make_filled(n, 16777215)
  return visit(r, 16777215, adj2, parents)

def make_empty(n):
  if n == 0:
    return []
  else:
    return List/Cons([], make_empty(n - 1))

def make_filled(n, value):
  if n == 0:
    return []
  else:
    return List/Cons(value, make_filled(n - 1))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
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
      u_neighbors = get_at(adj, u)
      adj1 = replace_at(adj, u, List/Cons(v, u_neighbors))
      v_neighbors = get_at(adj1, v)
      adj2 = replace_at(adj1, v, List/Cons(u, v_neighbors))
      return build_adj(edges.tail, adj2)

def visit(u, p, adj, parents):
  neighbors = get_at(adj, u)
  return visit_neighbors(neighbors, u, p, adj, parents)

def visit_neighbors(neighbors, u, p, adj, parents):
  match neighbors:
    case List/Nil:
      return parents
    case List/Cons:
      v = neighbors.head
      if v == p:
        return visit_neighbors(neighbors.tail, u, p, adj, parents)
      else:
        parents1 = replace_at(parents, v, u)
        parents2 = visit(v, u, adj, parents1)
        return visit_neighbors(neighbors.tail, u, p, adj, parents2)
