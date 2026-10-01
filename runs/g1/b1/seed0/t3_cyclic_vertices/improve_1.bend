def prog(x):
  (n, edges) = x
  adj = build_adj(0, n, edges, 0)
  rev = build_adj(0, n, edges, 1)
  (seen, order) = finish_roots(0, n, [], [], adj)
  return count_components(order, [], rev, 0)

def build_adj(i, n, edges, reverse):
  if i == n:
    return []
  else:
    row = outgoing(i, edges, reverse, [])
    rest = build_adj(i + 1, n, edges, reverse)
    return List/Cons(row, rest)

def outgoing(node, edges, reverse, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      if reverse == 0:
        if u == node:
          return outgoing(node, edges.tail, reverse, List/Cons(v, acc))
        else:
          return outgoing(node, edges.tail, reverse, acc)
      else:
        if v == node:
          return outgoing(node, edges.tail, reverse, List/Cons(u, acc))
        else:
          return outgoing(node, edges.tail, reverse, acc)

def get_row(rows, idx):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return rows.head
      else:
        return get_row(rows.tail, idx - 1)

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def finish_roots(i, n, seen, order, adj):
  if i == n:
    return (seen, order)
  else:
    (seen2, order2) = finish_dfs(i, seen, order, adj)
    return finish_roots(i + 1, n, seen2, order2, adj)

def finish_dfs(v, seen, order, adj):
  if contains(seen, v) == 1:
    return (seen, order)
  else:
    seen2 = List/Cons(v, seen)
    row = get_row(adj, v)
    (seen3, order2) = finish_neighbors(row, seen2, order, adj)
    return (seen3, List/Cons(v, order2))

def finish_neighbors(xs, seen, order, adj):
  match xs:
    case List/Nil:
      return (seen, order)
    case List/Cons:
      (seen2, order2) = finish_dfs(xs.head, seen, order, adj)
      return finish_neighbors(xs.tail, seen2, order2, adj)

def count_components(order, seen, rev, acc):
  match order:
    case List/Nil:
      return acc
    case List/Cons:
      v = order.head
      if contains(seen, v) == 1:
        return count_components(order.tail, seen, rev, acc)
      else:
        (seen2, size) = mark_component(v, seen, rev)
        if size > 1:
          return count_components(order.tail, seen2, rev, acc + size)
        else:
          return count_components(order.tail, seen2, rev, acc)

def mark_component(v, seen, adj):
  if contains(seen, v) == 1:
    return (seen, 0)
  else:
    seen2 = List/Cons(v, seen)
    row = get_row(adj, v)
    (seen3, size) = mark_neighbors(row, seen2, adj)
    return (seen3, size + 1)

def mark_neighbors(xs, seen, adj):
  match xs:
    case List/Nil:
      return (seen, 0)
    case List/Cons:
      (seen2, size1) = mark_component(xs.head, seen, adj)
      (seen3, size2) = mark_neighbors(xs.tail, seen2, adj)
      return (seen3, size1 + size2)
