def prog(x):
  (n, edges) = x
  if n <= 1:
    return 0
  else:
    adj = make_adj(n, 0)
    adj2 = add_edges(adj, edges)
    return all_sources(adj2, n, 0, 0)

def make_adj(n, i):
  if i < n:
    return List/Cons([], make_adj(n, i + 1))
  else:
    return []

def get_adj(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_adj(xs.tail, i - 1)

def set_adj(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_adj(xs.tail, i - 1, value))

def add_edges(adj, edges):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      ns_u = get_adj(adj, u)
      ns_v = get_adj(adj, v)
      adj1 = set_adj(adj, u, List/Cons(v, ns_u))
      adj2 = set_adj(adj1, v, List/Cons(u, ns_v))
      return add_edges(adj2, edges.tail)

def make_nums(n, i, value):
  if i < n:
    return List/Cons(value, make_nums(n, i + 1, value))
  else:
    return []

def get_num(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_num(xs.tail, i - 1)

def set_num(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_num(xs.tail, i - 1, value))

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))

def visit_neighbors(ns, ds, rear, distance, sentinel):
  match ns:
    case List/Nil:
      return (ds, rear)
    case List/Cons:
      v = ns.head
      old = get_num(ds, v)
      if old == sentinel:
        ds2 = set_num(ds, v, distance + 1)
        rear2 = List/Cons(v, rear)
        return visit_neighbors(ns.tail, ds2, rear2, distance, sentinel)
      else:
        return visit_neighbors(ns.tail, ds, rear, distance, sentinel)

def bfs(adj, ds, front, rear, sentinel):
  match front:
    case List/Nil:
      match rear:
        case List/Nil:
          return ds
        case List/Cons:
          front2 = reverse_acc(rear, [])
          return bfs(adj, ds, front2, [], sentinel)
    case List/Cons:
      u = front.head
      distance = get_num(ds, u)
      ns = get_adj(adj, u)
      (ds2, rear2) = visit_neighbors(ns, ds, rear, distance, sentinel)
      return bfs(adj, ds2, front.tail, rear2, sentinel)

def sum_range(ds, i, n, acc):
  if i < n:
    distance = get_num(ds, i)
    return sum_range(ds, i + 1, n, acc + distance)
  else:
    return acc

def all_sources(adj, n, source, acc):
  if source < n:
    sentinel = n + 1
    ds0 = make_nums(n, 0, sentinel)
    ds1 = set_num(ds0, source, 0)
    ds2 = bfs(adj, ds1, List/Cons(source, []), [], sentinel)
    total = sum_range(ds2, source + 1, n, 0)
    return all_sources(adj, n, source + 1, acc + total)
  else:
    return acc
