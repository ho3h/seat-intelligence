def prog(x):
  (n, queries, edges) = x
  adj0 = make_adj_lists(n)
  adj = build_adj(edges, adj0)
  chunks = num_chunks(n)
  bits = make_zero_chunks(chunks)
  return solve_queries(queries, adj, bits, [])

def num_chunks(n):
  whole = n / 24
  if n % 24 == 0:
    return whole
  else:
    return whole + 1

def make_adj_lists(n):
  if n == 0:
    return []
  else:
    return List/Cons([], make_adj_lists(n - 1))

def build_adj(edges, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      neighbors = get_adj(u, adj)
      adj2 = set_adj(u, List/Cons(v, neighbors), adj)
      return build_adj(edges.tail, adj2)

def get_adj(i, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_adj(i - 1, xs.tail)

def set_adj(i, value, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        tail2 = set_adj(i - 1, value, xs.tail)
        return List/Cons(xs.head, tail2)

def make_zero_chunks(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, make_zero_chunks(n - 1))

def get_chunk(i, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_chunk(i - 1, xs.tail)

def set_chunk(i, value, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        tail2 = set_chunk(i - 1, value, xs.tail)
        return List/Cons(xs.head, tail2)

def bit_has(bits, vertex):
  chunk = get_chunk(vertex / 24, bits)
  mask = 1 << (vertex % 24)
  present = chunk & mask
  if present != 0:
    return 1
  else:
    return 0

def bit_add(bits, vertex):
  index = vertex / 24
  chunk = get_chunk(index, bits)
  mask = 1 << (vertex % 24)
  updated = chunk | mask
  return set_chunk(index, updated, bits)

def prepend_all(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return List/Cons(xs.head, prepend_all(xs.tail, acc))

def reachable(a, b, adj, bits):
  if a == b:
    return 1
  else:
    return search_reach(b, adj, bits, List/Cons(a, []))

def search_reach(target, adj, seen, todo):
  match todo:
    case List/Nil:
      return 0
    case List/Cons:
      node = todo.head
      rest = todo.tail
      if node == target:
        return 1
      else:
        already = bit_has(seen, node)
        if already == 1:
          return search_reach(target, adj, seen, rest)
        else:
          seen2 = bit_add(seen, node)
          neighbors = get_adj(node, adj)
          todo2 = prepend_all(neighbors, rest)
          return search_reach(target, adj, seen2, todo2)

def solve_queries(queries, adj, bits, acc):
  match queries:
    case List/Nil:
      return reverse_list(acc)
    case List/Cons:
      (a, b) = queries.head
      answer = reachable(a, b, adj, bits)
      return solve_queries(queries.tail, adj, bits, List/Cons(answer, acc))

def reverse_list(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))
