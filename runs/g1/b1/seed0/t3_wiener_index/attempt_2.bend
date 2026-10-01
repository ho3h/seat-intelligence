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

def mark_seen(seen, v):
  block = v / 24
  bit = 1 << (v % 24)
  old = get_num(seen, block)
  return set_num(seen, block, old | bit)

def visit_neighbors(ns, seen, rear, distance, source, total):
  match ns:
    case List/Nil:
      return (seen, rear, total)
    case List/Cons:
      v = ns.head
      block = v / 24
      bit = 1 << (v % 24)
      old = get_num(seen, block)
      if (old & bit) == 0:
        seen2 = set_num(seen, block, old | bit)
        rear2 = List/Cons((v, distance + 1), rear)
        if v > source:
          return visit_neighbors(ns.tail, seen2, rear2, distance, source, total + distance + 1)
        else:
          return visit_neighbors(ns.tail, seen2, rear2, distance, source, total)
      else:
        return visit_neighbors(ns.tail, seen, rear, distance, source, total)

def bfs(adj, seen, front, rear, source, total):
  match front:
    case List/Nil:
      match rear:
        case List/Nil:
          return total
        case List/Cons:
          front2 = reverse_acc(rear, [])
          return bfs(adj, seen, front2, [], source, total)
    case List/Cons:
      (u, distance) = front.head
      ns = get_adj(adj, u)
      (seen2, rear2, total2) = visit_neighbors(ns, seen, rear, distance, source, total)
      return bfs(adj, seen2, front.tail, rear2, source, total2)

def all_sources(adj, n, source, acc):
  if source < n:
    blocks = (n + 23) / 24
    seen0 = make_nums(blocks, 0, 0)
    seen1 = mark_seen(seen0, source)
    total = bfs(adj, seen1, List/Cons((source, 0), []), [], source, 0)
    return all_sources(adj, n, source + 1, acc + total)
  else:
    return acc
