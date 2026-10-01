def prog(x):
  (n, edges) = x
  adj = build_adj(0, n, edges)
  return count_cyclic(0, n, adj, 0)

def build_adj(i, n, edges):
  if i == n:
    return []
  else:
    row = outgoing(i, edges, [])
    rest = build_adj(i + 1, n, edges)
    return List/Cons(row, rest)

def outgoing(node, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      if u == node:
        return outgoing(node, edges.tail, List/Cons(v, acc))
      else:
        return outgoing(node, edges.tail, acc)

def get_row(rows, idx):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return rows.head
      else:
        return get_row(rows.tail, idx - 1)

def push_all(xs, stack):
  match xs:
    case List/Nil:
      return stack
    case List/Cons:
      return push_all(xs.tail, List/Cons(xs.head, stack))

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def search(src, todo, seen, adj):
  match todo:
    case List/Nil:
      return 0
    case List/Cons:
      v = todo.head
      if v == src:
        return 1
      else:
        if contains(seen, v) == 1:
          return search(src, todo.tail, seen, adj)
        else:
          next = push_all(get_row(adj, v), todo.tail)
          return search(src, next, List/Cons(v, seen), adj)

def count_cyclic(i, n, adj, acc):
  if i == n:
    return acc
  else:
    todo = push_all(get_row(adj, i), [])
    if search(i, todo, [], adj) == 1:
      return count_cyclic(i + 1, n, adj, acc + 1)
    else:
      return count_cyclic(i + 1, n, adj, acc)
