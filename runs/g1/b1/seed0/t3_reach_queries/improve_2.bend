def prog(x):
  (n, queries, edges) = x
  match queries:
    case List/Nil:
      return []
    case List/Cons:
      adj0 = make_adj_lists(n)
      adj = build_adj(edges, adj0)
      chunks = num_chunks(n)
      return answer_queries(queries, adj, chunks)

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
  if chunk & mask == 0:
    return 0
  else:
    return 1

def bit_add(bits, vertex):
  index = vertex / 24
  chunk = get_chunk(index, bits)
  mask = 1 << (vertex % 24)
  return set_chunk(index, chunk | mask, bits)

def reachable(a, b, adj, chunks):
  if a == b:
    return 1
  else:
    seen = bit_add(make_zero_chunks(chunks), a)
    return search_reach(b, adj, seen, List/Cons(a, []))

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
        neighbors = get_adj(node, adj)
        (found, seen2, todo2) = expand_neighbors(neighbors, target, seen, rest)
        if found == 1:
          return 1
        else:
          return search_reach(target, adj, seen2, todo2)

def expand_neighbors(neighbors, target, seen, todo):
  match neighbors:
    case List/Nil:
      return (0, seen, todo)
    case List/Cons:
      neighbor = neighbors.head
      if neighbor == target:
        return (1, seen, todo)
      else:
        if bit_has(seen, neighbor) == 1:
          return expand_neighbors(neighbors.tail, target, seen, todo)
        else:
          seen2 = bit_add(seen, neighbor)
          todo2 = List/Cons(neighbor, todo)
          return expand_neighbors(neighbors.tail, target, seen2, todo2)

def answer_queries(queries, adj, chunks):
  match queries:
    case List/Nil:
      return []
    case List/Cons:
      (a, b) = queries.head
      answer = reachable(a, b, adj, chunks)
      rest = answer_queries(queries.tail, adj, chunks)
      return List/Cons(answer, rest)
