def prog(x):
  (n, edges) = x
  (adj, rev) = build_adjs(0, n, edges)
  bits = make_bits(0, n)
  (seen, order) = finish_roots(0, n, bits, [], adj)
  return count_components(order, bits, rev, 0)

def make_bits(i, n):
  if i >= n:
    return []
  else:
    return List/Cons(0, make_bits(i + 24, n))

def get_word(bits, idx):
  match bits:
    case List/Nil:
      return 0
    case List/Cons:
      if idx == 0:
        return bits.head
      else:
        return get_word(bits.tail, idx - 1)

def set_word(bits, idx, value):
  match bits:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return List/Cons(value, bits.tail)
      else:
        return List/Cons(bits.head, set_word(bits.tail, idx - 1, value))

def marked(bits, v):
  word = get_word(bits, v / 24)
  mask = 1 << (v % 24)
  if (word & mask) == 0:
    return 0
  else:
    return 1

def mark(bits, v):
  idx = v / 24
  word = get_word(bits, idx)
  mask = 1 << (v % 24)
  return set_word(bits, idx, word | mask)

def build_adjs(i, n, edges):
  if i == n:
    return ([], [])
  else:
    (out, incoming) = outgoing_both(i, edges, [], [])
    (adj, rev) = build_adjs(i + 1, n, edges)
    return (List/Cons(out, adj), List/Cons(incoming, rev))

def outgoing_both(node, edges, out, incoming):
  match edges:
    case List/Nil:
      return (out, incoming)
    case List/Cons:
      (u, v) = edges.head
      if u == node:
        return outgoing_both(node, edges.tail, List/Cons(v, out), incoming)
      else:
        if v == node:
          return outgoing_both(node, edges.tail, out, List/Cons(u, incoming))
        else:
          return outgoing_both(node, edges.tail, out, incoming)

def get_row(rows, idx):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return rows.head
      else:
        return get_row(rows.tail, idx - 1)

def finish_roots(i, n, seen, order, adj):
  if i == n:
    return (seen, order)
  else:
    (seen2, order2) = finish_dfs(i, seen, order, adj)
    return finish_roots(i + 1, n, seen2, order2, adj)

def finish_dfs(v, seen, order, adj):
  if marked(seen, v) == 1:
    return (seen, order)
  else:
    seen2 = mark(seen, v)
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
      if marked(seen, v) == 1:
        return count_components(order.tail, seen, rev, acc)
      else:
        (seen2, size) = mark_component(v, seen, rev)
        if size > 1:
          return count_components(order.tail, seen2, rev, acc + size)
        else:
          return count_components(order.tail, seen2, rev, acc)

def mark_component(v, seen, adj):
  if marked(seen, v) == 1:
    return (seen, 0)
  else:
    seen2 = mark(seen, v)
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
